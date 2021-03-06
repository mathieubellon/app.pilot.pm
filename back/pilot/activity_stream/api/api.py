from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from pilot.activity_stream.api.serializers import ActivitySerializer
from pilot.activity_stream.comment import create_comment_and_activity
from pilot.activity_stream.models import Activity
from pilot.notifications.notify import process_notifications_when_comment_is_updated
from pilot.utils import api as api_utils


class ActivityPagination(api_utils.PilotPageNumberPagination):
    page_size = 10


@method_decorator(name='list', decorator=swagger_auto_schema(operation_summary="List activities"))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(operation_summary="Get a single activity"))
class ActivityViewSet(api_utils.GenericObjectMixin,
                      viewsets.ReadOnlyModelViewSet):
    """
    An activity represents one action made into the software in the past,
    stored to understand the history.

    The activities are generated by the backend, and are always read-only.

    Comments are an integral part of the activity API.

    There are 4 main components of an activity :
    - The actor is the entity who performed the activity
    - The target is the object where the activity took place
    - The verb is the action performed
    - The action object is an optional object concerned by the verb ( example : a comment made on the target )
    """

    permission_classes = [
        api_utils.DeskPermission
    ]
    model = Activity
    serializer_class = ActivitySerializer
    pagination_class = ActivityPagination

    def get_queryset(self):
        request = self.request
        desk = request.desk
        activities = (
            Activity.objects.get_permited_activities(desk, request.user)
            .select_related('actor')
            .prefetch_related('action_object', 'target')
        )

        content_type_id = self.get_generic_content_type_id()
        if content_type_id:
            activities = activities.filter(target_content_type_id=content_type_id)

        object_id = self.get_generic_object_id()
        if object_id:
            activities = activities.filter(target_object_id=object_id)

        # If we're not looking at a specific instance, we don't send back the comment activities
        if not object_id:
            activities = activities.exclude(verb=Activity.VERB_COMMENTED)

        return activities

    def paginate_queryset(self, queryset):
        # We only paginate for the global activity stream (dashboard),
        # where all activities are mixed.
        paginated = self.request.query_params.get('paginated', True) != 'false'
        if paginated:
            return super(ActivityViewSet, self).paginate_queryset(queryset)
        else:
            return None

    @swagger_auto_schema(
        operation_summary="Create a comment",
        request_body=openapi.Schema(type='object', properties=dict(
            comment_content=openapi.Schema(type='prosemirror'),
            content_type_id=openapi.Schema(type='integer'),
            object_id=openapi.Schema(type='integer'),
        )),
        responses={status.HTTP_201_CREATED: ActivitySerializer}
    )
    @action(detail=False, methods=['POST'])
    def create_comment(self, request, *args, **kwargs):
        instance = self.get_generic_object()
        comment_content = request.data.get('comment_content', {})

        activity = create_comment_and_activity(
            instance=instance,
            comment_content=comment_content,
            user=self.request.user
        )

        serializer = self.get_serializer(activity)
        return Response(serializer.data, status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Edit a comment",
        request_body=openapi.Schema(type='object', properties=dict(
            activity_id=openapi.Schema(type='integer'),
            comment_content=openapi.Schema(type='prosemirror')
        )),
        responses={status.HTTP_200_OK: ActivitySerializer}
    )
    @action(detail=False, methods=['POST'])
    def edit_comment(self, request, *args, **kwargs):
        activity = Activity.objects.get(id=request.data.get('activity_id'))
        if not activity.is_comment:
            raise HttpResponseBadRequest("Activity is not a comment")

        comment = activity.action_object

        if comment.user != request.user:
            raise HttpResponseBadRequest("Only the author can edit a comment")

        comment_content_before = comment.comment_content
        comment.comment_content = request.data.get('comment_content', {})
        comment.edition_date = timezone.now()
        comment.save()

        process_notifications_when_comment_is_updated(comment, comment_content_before)

        serializer = self.get_serializer(activity)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Delete a comment",
        request_body=openapi.Schema(type='object', properties=dict(
            activity_id=openapi.Schema(type='integer')
        )),
        responses={status.HTTP_200_OK: ActivitySerializer}
    )
    @action(detail=False, methods=['POST'])
    def delete_comment(self, request, *args, **kwargs):
        activity = Activity.objects.get(id=request.data.get('activity_id'))
        if not activity.is_comment:
            raise HttpResponseBadRequest("Activity is not a comment")

        comment = activity.action_object

        if comment.user != request.user:
            raise HttpResponseBadRequest("Only the author can delete a comment")

        comment.comment_content = {}
        comment.deletion_date = timezone.now()
        comment.save()

        serializer = self.get_serializer(activity)
        return Response(serializer.data)
