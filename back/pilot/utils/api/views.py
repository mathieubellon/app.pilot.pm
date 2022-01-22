from django.conf import settings
from django.db import transaction
from django.http import QueryDict, HttpResponseBadRequest
from django.http.response import Http404
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status

from pilot.activity_stream.models import Activity
from pilot.activity_stream.jobs import create_activity
from pilot.sharings.models import Sharing, SharingType
from pilot.utils.diff import DiffTracker


csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())
never_cache_m = method_decorator(never_cache)

class ActivityModelMixin(object):
    """
    Extended mixin of the DRF UpdateModelMixin that send an activity_stream notification
    """
    activity_anonymous_user = Activity.PUBLIC_API_USER

    activity_create_verb = Activity.VERB_CREATED
    activity_create_action_object = None

    activity_update_verb = Activity.VERB_UPDATED
    activity_update_action_object = None

    activity_delete_verb = Activity.VERB_DELETED
    activity_delete_action_object = None

    # ===================
    # Create zone
    # ===================

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            self.perform_create(serializer)
            self.create_activity_for_create(serializer.instance)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def create_activity_for_create(self, instance):
        self.create_activity(**dict(
            verb=self.get_activity_create_verb(instance),
            target=self.get_activity_create_target(instance),
            action_object=self.get_activity_create_action_object(instance)
        ))

    def get_activity_create_verb(self, instance):
        return self.activity_create_verb

    def get_activity_create_target(self, instance):
        return instance

    def get_activity_create_action_object(self, instance):
        return self.activity_create_action_object

    # ===================
    # Update zone
    # ===================

    def update_instance(self, instance, data, partial):
        diff_tracker = DiffTracker(instance)

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            self.perform_update(serializer)
            self.create_activity_for_update(serializer.instance, diff_tracker)

        return serializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        self.update_instance(
            instance=instance,
            data=request.data,
            partial=partial
        )

        # Reload the instance so we have an up-to-date representation in the serializer
        instance = self.get_object()
        return Response(self.get_serializer(instance).data)

    def create_activity_for_update(self, instance, diff_tracker):
        self.create_activity(**dict(
            verb=self.get_activity_update_verb(instance),
            target=self.get_activity_update_target(instance),
            diff=diff_tracker.get_diff(instance),
            action_object=self.get_activity_update_action_object(instance)
        ))

    def get_activity_update_verb(self, instance):
        return self.activity_update_verb

    def get_activity_update_target(self, instance):
        return instance

    def get_activity_update_action_object(self, instance):
        return self.activity_update_action_object

    # ===================
    # Delete zone
    # ===================

    def destroy_instance(self, instance):
        # We need to create the activity before the deletion,
        # so the target instance still has an id for its display string
        with transaction.atomic():
            self.create_activity_for_delete(instance)
            self.perform_destroy(instance)

    def destroy(self, request, *args, **kwargs):
        self.destroy_instance(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create_activity_for_delete(self, instance):
        self.create_activity(**dict(
            verb=self.get_activity_delete_verb(instance),
            target=self.get_activity_delete_target(instance),
            action_object=self.get_activity_delete_action_object(instance)
        ))

    def get_activity_delete_verb(self, instance):
        return self.activity_delete_verb

    def get_activity_delete_target(self, instance):
        return instance

    def get_activity_delete_action_object(self, instance):
        return self.activity_delete_action_object

    # ===================
    # Common
    # ===================

    def create_activity(self, **activity_kwargs):
        default_activity_kwargs = dict(
            actor=self.get_actor(),
            desk=self.request.desk
        )
        default_activity_kwargs.update(activity_kwargs)
        create_activity(**default_activity_kwargs)

    def get_actor(self):
        # On the public API, the user will be anonymous
        return self.activity_anonymous_user if self.request.user.is_anonymous else self.request.user


class BulkActionMixin(object):
    def get_bulk_action_handlers(self):
        return {}

    @action(detail=False, methods=['POST'])
    def bulk_action(self, request, *args, **kwargs):
        ids = request.data.pop('ids', [])
        action = request.data.pop('action', None)
        params = request.data.pop('params', {})

        action_handler = self.get_bulk_action_handlers().get(action)
        if not action_handler:
            return HttpResponseBadRequest("Unknown action {}".format(action))

        if ids == '__ALL__':
            queryset = self.filter_queryset(self.get_queryset())
        else:
            if len(ids) == 0:
                return HttpResponseBadRequest("At least one id is required")

            queryset = self.get_queryset().filter(id__in=ids)

        with transaction.atomic():
            for instance in queryset:
                action_handler(instance, params)

        return Response(status=status.HTTP_204_NO_CONTENT)


class GenericObjectMixin(object):
    """
    A mixin for views that make generic operations on an object
    linked through object_id / content_type_id

    Two parameters are needed to lookup the generic object:
     * The id of the content_type
     * The id of the object of this content_type

    These parameters are searched into the kwargs (from the url), then into the request params (POST or GET).
    The default names for these parameters are :
     * content_type_id
     * object_id
    """
    content_type_id_param_name = 'content_type_id'
    object_id_param_name = 'object_id'
    content_type = None

    def get_generic_content_type_id(self):
        content_type_id = self.kwargs.get(
            self.content_type_id_param_name,
            self.request.data.get(
                self.content_type_id_param_name,
                self.request.query_params.get(self.content_type_id_param_name)
            )
        )
        try:
            return int(content_type_id)
        except (ValueError, TypeError):
            return None

    def get_generic_object_id(self):
        object_id = self.kwargs.get(
            self.object_id_param_name,
            self.request.data.get(
                self.object_id_param_name,
                self.request.query_params.get(self.object_id_param_name)
            )
        )
        try:
            return int(object_id)
        except (ValueError, TypeError):
            return None

    def get_generic_object(self):
        content_type_id = self.get_generic_content_type_id()
        object_id = self.get_generic_object_id()

        try:
            self.content_type = ContentType.objects.get_for_id(content_type_id)
            return self.content_type.get_object_for_this_type(id=object_id, desk=self.request.desk)
        except ObjectDoesNotExist:
            raise Http404()


class SharedApiMixin(object):
    """
    A mixin for API views that are an endpoint of a shared list.

    Set the desk of the request to the desk of the shared token.
    Ensure that the password was provided, if the shared list is protected by a password.
    Restrict the visible objects to the parameters specified in the shared token.
    """
    token_param_name = 'token'

    def initial(self, request, *args, **kwargs):
        super(SharedApiMixin, self).initial(request, *args, **kwargs)

        self.sharing = self.get_sharing()
        self.ensure_password()

        self.request.desk = self.sharing.desk

        self.apply_token_query_params()

    def get_sharing(self):
        """
        Get the sharing defined by the url params token
        """
        try:
            return Sharing.objects.get(
                token=self.kwargs[self.token_param_name]
            )
        except Sharing.DoesNotExist:
            raise Http404

    def ensure_password(self):
        """
        Ensure that the password was provided, if the sharing is protected by a password.
        """
        if not self.sharing.password:
            return

        checked_sharing_id = self.request.session.get(settings.SHARING_PASSWORD_CHECKED)
        if checked_sharing_id != self.sharing.id:
            raise PermissionDenied()

    def apply_token_query_params(self):
        """
        Force the use the saved filters whatever are the query param in the url, to prevent data leakage
        """
        filter_params = QueryDict(query_string=self.sharing.get_query_string(), mutable=True)
        # Shared calendar should show items from any period, not only the ones at the filer creation
        if self.sharing.type == SharingType.CALENDAR:
            start, end = self.request.query_params.get('start'), self.request.query_params.get('end')
            if start and end:
                filter_params['start'] = self.request.query_params.get('start')
                filter_params['end'] = self.request.query_params.get('end')

        # Allow the page params to pass through
        page = self.request.query_params.get('page')
        if page:
            filter_params['page'] = page

        # Override the request query dict with the one from the shared token
        # This is what will be used on a call to self.request.query_params
        self.request._request.GET = filter_params
