import uuid

from django.contrib.auth import update_session_auth_hash
from django.db import transaction
from django.db.models import Subquery, OuterRef, Prefetch
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework import viewsets
from rest_framework.decorators import action

import django_filters
from django_filters.rest_framework import FilterSet

from pilot.accounts.subscription import update_stripe_subscription_items
from pilot.accounts.usage_limit import UserUsageLimit, UsageLimitReached
from pilot.comments.jobs import MentionUpdateJob
from pilot.messaging.models import UserMessage
from pilot.notifications import emailing
from pilot.notifications.models import Notification
from pilot.pilot_users.api.serializers import ChangeNotificationPreferenceSerializer, ChangePasswordSerializer, \
    PilotInvitationSerializer, \
    PilotUserLightSerializer, PilotUserMeSerializer, PilotUserSerializer, TeamSerializer
from pilot.pilot_users.jobs import AllUsersXLSExportJob
from pilot.pilot_users.models import InvitationToken, PilotUser, Team, UserInDesk, UserInDeskDeactivated
from pilot.utils import api as api_utils
from pilot.utils.s3 import get_s3_signature_v4


class PilotUserFilter(FilterSet):
    teams = django_filters.ModelMultipleChoiceFilter(queryset=Team.objects.all())
    Xteams = django_filters.ModelMultipleChoiceFilter(field_name='teams', queryset=Team.objects.all(), exclude=True)
    username = django_filters.CharFilter(lookup_expr='icontains')

    order_by = django_filters.OrderingFilter(
        fields=('id', 'username')
    )

    class Meta:
        model = PilotUser
        fields = ('username', 'teams', 'Xteams')


class InvitationViewSet(viewsets.mixins.CreateModelMixin,
                        viewsets.mixins.RetrieveModelMixin,
                        viewsets.mixins.DestroyModelMixin,
                        viewsets.mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    A viewset to work with Invitation Token
    """
    serializer_class = PilotInvitationSerializer
    permission_classes = [
        api_utils.DeskPermission,
        api_utils.IsAdminOrReadOnlyPermission
    ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        if (InvitationToken.objects.filter(email=email, desk=request.desk).exists() or
           PilotUser.objects.filter(email=email, desks=request.desk).exists()):
            return Response(_('Email déjà existant sur ce desk'), status=status.HTTP_403_FORBIDDEN)

        try:
            UserUsageLimit(request.desk).check_limit()
        except UsageLimitReached as e:
            return Response(str(e), status=status.HTTP_403_FORBIDDEN)

        serializer.save(
            created_by=request.user,
            desk=request.desk
        )
        emailing.send_invitation_token(serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return (InvitationToken.objects
                .filter(desk=self.request.desk)
                .filter(used=False)
                .order_by('email'))


    @action(detail=True, methods=['POST'])
    def send_again(self, request, *args, **kwargs):
        emailing.send_invitation_token(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)


class UsersMeViewSet(viewsets.mixins.RetrieveModelMixin,
                     viewsets.mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    """
    A viewset to work with the currently connected user ("me")
    """
    serializer_class = PilotUserMeSerializer
    permission_classes = [
        api_utils.DeskPermission
    ]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        avatar_kwargs = {}
        # The avatar param may be present or not, and if present in may be null.
        avatar = self.request.data.get('avatar')
        if avatar:
            # In case of a delete, we'll get 'DELETE'
            if avatar == 'DELETE':
                avatar_kwargs['avatar'] = None

            # In case of a user update, the avatar field may have been updated,
            # or it may stay the same ( if we're updating another field )
            # In case of an update not related to the avatar, we'll get the full url
            # (with https:// and the S3 domaine name )
            # If it's an actual avatar update, we'll get only a S3 key.
            # Thus, we only trigger an update if we the value doesn't starts with an https:// protocol
            # We also exclude the data:image that is set by PilotAvatarMixin in working environment.
            elif not (avatar.startswith('https://') or avatar.startswith('data:image')):
                avatar_kwargs['avatar'] = avatar

        user = serializer.instance
        old_username = user.username

        serializer.save(
            updated_by=self.request.user,
            **avatar_kwargs
        )

        if user.username != old_username:
            MentionUpdateJob.launch_r(self.request, user)

    @action(detail=True, methods=['POST'], serializer_class=ChangePasswordSerializer)
    def change_password(self, request, *args, **kwargs):
        response = self.update(request, *args, **kwargs)
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(request, self.request.user)
        return response

    @action(detail=True, methods=['POST'])
    def get_s3_signature_for_avatar(self, request):
        # Generate a random uuid for the file name, to avoid guessing by desk id
        s3_path = 'avatar/{0}'.format(uuid.uuid4())
        content_type = request.data.get('contentType')
        signature_data = get_s3_signature_v4(s3_path, content_type)
        return JsonResponse(signature_data)

    @action(detail=True, methods=['POST'])
    def set_message_as_read(self, request):
        UserMessage.objects.filter(
            user=request.user,
            message_id=request.data.get('message_id')
        ).update(read_at=timezone.now())
        return Response()


class UsersViewSet(viewsets.mixins.RetrieveModelMixin,
                   viewsets.mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """
    A viewset to work with users endpoint
    """
    serializer_class = PilotUserSerializer
    permission_classes = [
        api_utils.DeskPermission,
        api_utils.IsAdminOrReadOnlyPermission
    ]
    filter_class = PilotUserFilter
    default_ordering = 'username'
    deactivated_users = False

    def get_queryset(self):
        queryset = (
            PilotUser.objects
            # VERY IMPORTANT : Filter the teams to keep only those of the current desk.
            # ALso optimize by prefeteching the M2M relationship.
            .prefetch_related(Prefetch('teams', queryset=Team.objects.filter(desk=self.request.desk)))
            # Default ordering, that may be overrided by the query params
            .order_by(self.default_ordering)
        )

        if self.deactivated_users:
            queryset = queryset.filter(desks_deactivated=self.request.desk)
        else:
            queryset = queryset.filter(desks=self.request.desk)

        if not self.deactivated_users:
            user_in_desk = UserInDesk.objects.filter(desk=self.request.desk, user=OuterRef('id'))
            queryset = queryset.annotate(permission=Subquery(user_in_desk.values('permission')))

        return queryset

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @action(detail=False, serializer_class=PilotUserLightSerializer)
    def choices(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(detail=False, deactivated_users=True)
    def deactivated(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(detail=False, methods=['PUT'])
    def export(self, request, *args, **kwargs):
        AllUsersXLSExportJob.launch_r(self.request, timeout='30m')
        return Response(status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['PUT'])
    def update_permission(self, request, *args, **kwargs):
        user = self.get_object()
        permission = request.data['permission']
 
        if user.id == request.user.id:
            return Response(_("Vous ne pouvez pas changer vos propres permissions"), status=status.HTTP_403_FORBIDDEN)

        UserInDesk.objects.filter(
            user=user,
            desk=request.desk
        ).update(permission=permission)
        user.permission = permission  # Add the permission for the serialzier
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=['PUT'])
    def update_teams(self, request, *args, **kwargs):
        user = self.get_object()
        teams_id = request.data['teams_id']

        # Remove all the user's teams FROM THE CURRENT DESK
        user.teams.through.objects.filter(team__desk=request.desk, pilotuser=user).delete()
        # Add the newly selected teams
        for team in Team.objects.filter(desk=request.desk, id__in=teams_id):
            user.teams.add(team)

        # Update the teams value for the response
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=['PUT'])
    def deactivate(self, request, *args, **kwargs):
        user = self.get_object()

        if user.id == request.user.id:
            return Response(_("Vous ne pouvez pas désactiver votre propre compte"), status=status.HTTP_403_FORBIDDEN)

        user_in_desk = get_object_or_404(UserInDesk, user=user, desk=request.desk)

        with transaction.atomic():
            UserInDeskDeactivated.objects.create(
                desk=user_in_desk.desk,
                user=user_in_desk.user,
                permission=user_in_desk.permission,
                config_dashboard=user_in_desk.config_dashboard,
                config_calendar=user_in_desk.config_calendar,
            )
            user_in_desk.delete()

        # When the number of active user change, we need to update the billing amount
        update_stripe_subscription_items(request.organization)

        return Response(self.get_serializer(user).data)

    @action(detail=True, methods=['PUT'], deactivated_users=True)
    def reactivate(self, request, *args, **kwargs):
        # Re-activation : need to check the limit
        try:
            UserUsageLimit(request.desk).check_limit()
        except UsageLimitReached as e:
            return Response(str(e), status=status.HTTP_403_FORBIDDEN)

        user = self.get_object()
        user_in_desk_deactivated = get_object_or_404(UserInDeskDeactivated, user=user, desk=request.desk)

        with transaction.atomic():
            UserInDesk.objects.create(
                desk=user_in_desk_deactivated.desk,
                user=user_in_desk_deactivated.user,
                permission=user_in_desk_deactivated.permission,
                config_dashboard=user_in_desk_deactivated.config_dashboard,
                config_calendar=user_in_desk_deactivated.config_calendar,
            )
            user_in_desk_deactivated.delete()

        # When the number of active user change, we need to update the billing amount
        update_stripe_subscription_items(request.organization)

        emailing.send_reactivated_user(user, request.desk, request.user)

        return Response(self.get_serializer(user).data)

    @action(detail=True, methods=['POST'], deactivated_users=True)
    def wipeout(self, request, *args, **kwargs):
        user = self.get_object()
        # Ensure the user is in this desk, deactivated
        current_user_in_desk = get_object_or_404(
            UserInDeskDeactivated,
            user=user,
            desk=self.request.desk
        )

        # Trigger the actual wipeout only if the user is not in another desk.
        # If he's still in another desk, just remove the link between the desk and the user.
        if (
            UserInDeskDeactivated.objects.filter(user=user).count() > 1 or
            UserInDesk.objects.filter(user=user).exists()
        ):
            current_user_in_desk.delete()
        else:
            user.wipeout()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserNotificationPreferenceUpdate(generics.UpdateAPIView):
    """
    An API view to update notification preference with a notification token ( without being authenticated )
    """
    serializer_class = ChangeNotificationPreferenceSerializer

    def get_object(self):
        token = self.kwargs['token']
        notification = get_object_or_404(Notification, token=token)
        return notification.to


class TeamViewSet(api_utils.ActivityModelMixin,
                  viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [
        api_utils.DeskPermission,
        api_utils.IsAdminOrReadOnlyPermission
    ]
    default_ordering = 'name'

    def get_queryset(self):
        return (Team.objects
                .filter(desk=self.request.desk)
                # Default ordering, that may be overrided by the query params
                .order_by(self.default_ordering))

    # ===================
    # Create / Update
    # ===================

    def perform_create(self, serializer):
        return serializer.save(
            desk=self.request.desk,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        team = serializer.instance
        old_name = team.name

        serializer.save(updated_by=self.request.user)

        if team.name != old_name:
            MentionUpdateJob.launch_r(self.request, team)

