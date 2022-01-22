from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from pilot.notifications.api.serializers import NotificationFeedSerializer, NotificationSerializer, ReminderSerializer
from pilot.notifications.models import Notification, NotificationFeed, Reminder
from pilot.utils import api as api_utils


class NotificationListPagination(api_utils.PilotPageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'


@method_decorator(name='list', decorator=swagger_auto_schema(operation_summary="List notifications"))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(operation_summary="Get a single notification"))
class NotificationViewSet(viewsets.mixins.UpdateModelMixin,
                          viewsets.ReadOnlyModelViewSet):
    """
    In-app notification for one user.

    Most of the notifications are related to one instance in the system,
    which is represented as a [Generic linked object](#section/Core-concepts/Generic-linked-object-serialization).
    Pay attention however than some notifications are not, for example data exports.

    The notification has two urls : the target url which is the actual url of the notificaton object,
    and its 'goto' url which redirects to the target url and is used in emails.

    The target url may be :
     - the url of its linked_object
     - a link to a resource ( an export file for example )
     - null ( if the linked_object has been deleted for example )

    If the target url is null, then the goto url will also be null.
    """

    serializer_class = NotificationSerializer
    permission_classes = [
        api_utils.DeskPermission
    ]
    pagination_class = NotificationListPagination
    base_queryset = Notification.objects
    # Set to True to query all the task of a user, whatever the desk
    cross_desk = False

    def get_queryset(self):
        queryset = (
            self.base_queryset
            .filter(to=self.request.user)
            .prefetch_related('linked_object')
            .order_by('-send_at')
        )
        if not self.cross_desk:
            queryset = queryset.filter(desk=self.request.desk)
        return queryset

    @swagger_auto_schema(
        operation_summary="List unread notifications",
    )
    @action(detail=False, base_queryset=Notification.unread_objects)
    def unread(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List read notifications",
    )
    @action(detail=False, base_queryset=Notification.read_objects)
    def read(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Set all notifications as read",
    )
    @action(detail=False, methods=['POST'])
    def set_all_read(self, request, *args, **kwargs):
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response()


class NotificationFeedViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationFeedSerializer
    permission_classes = [
        api_utils.DeskPermission
    ]

    def get_queryset(self):
        return NotificationFeed.objects.filter(
            desk=self.request.desk,
            user=self.request.user
        ).select_related('saved_filter').order_by('-id')

    def perform_create(self, serializer):
        serializer.save(
            desk=self.request.desk,
            user=self.request.user
        )


class ReminderViewSet(api_utils.GenericObjectMixin,
                      viewsets.ModelViewSet):
    serializer_class = ReminderSerializer
    permission_classes = [
        api_utils.DeskPermission
    ]

    def get_queryset(self):
        return Reminder.objects.filter(
            desk=self.request.desk,
            user=self.request.user
        )

    def perform_create(self, serializer):
        reminder = Reminder(
            desk=self.request.desk,
            user=self.request.user,
            **serializer.validated_data
        )
        reminder.set_target_for_creation(self.get_generic_object_id())
        # Tallying will also save the reminder, thus creating it here
        reminder.tally()

        # Update the serializer data for the response
        serializer._data = serializer.to_representation(reminder)
