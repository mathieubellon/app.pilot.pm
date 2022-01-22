from django.db import transaction
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden
from django.utils import timezone
from django.db.models import F as Field, Prefetch

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from pilot.activity_stream.models import Activity
from pilot.activity_stream.jobs import create_activity
from pilot.notifications.models import Reminder
from pilot.notifications.notify import notify_when_assigned_to_task, notify_when_task_todo, \
    notify_when_task_deleted, notify_when_my_task_updated
from pilot.tasks.api.serializers import TaskGroupSerializer, TaskSerializer, TaskTemplateSerializer
from pilot.tasks.api.serializers_base import LinkedTaskSerializer
from pilot.tasks.initial_tasks import import_task_group_on_instance
from pilot.tasks.models import Task, TaskGroup
from pilot.utils import api as api_utils
from pilot.utils.diff import DiffTracker


class TaskListPagination(api_utils.PilotPageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'


class TaskViewSet(api_utils.GenericObjectMixin,
                  viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [
        api_utils.DeskPermission
    ]
    pagination_class = TaskListPagination
    base_queryset = Task.objects
    # Set to True to query all the task of a user, whatever the desk
    cross_desk = False

    def get_queryset(self):
        # Prevent access to tasks templates through this ViewSet
        queryset = self.base_queryset.filter(task_group=None)
        if not self.cross_desk:
            queryset = queryset.filter(desk=self.request.desk)
        return queryset.distinct()

    def perform_create(self, serializer):
        linked_object = self.get_generic_object()

        with transaction.atomic():
            # Update other states order
            linked_object.tasks.update(order=Field('order')+1)

            # Create the new task
            task = serializer.save(
                desk=self.request.desk,
                created_by=self.request.user
            )
            linked_object.tasks.add(task)

        create_activity(
            actor=self.request.user,
            desk=self.request.desk,
            verb=Activity.VERB_TASK_CREATED,
            target=linked_object,
            action_object=task
        )

        notify_when_assigned_to_task(self.request.user, task, task.assignees.all())

        return task

    def perform_update(self, serializer):
        diff_tracker = DiffTracker(serializer.instance)
        is_done_before = serializer.instance.done
        is_done_after = serializer.validated_data.get('done')
        assignees_before = set(serializer.instance.assignees.all())

        save_kwargs = {}
        if not is_done_before and is_done_after:
            save_kwargs['done_by'] = self.request.user
            save_kwargs['done_at'] = timezone.now()
        if is_done_before and not is_done_after:
            save_kwargs['done_by'] = None
            save_kwargs['done_at'] = None

        with transaction.atomic():
            task = serializer.save(
                updated_by=self.request.user,
                **save_kwargs
            )
            # If the task has been defined as the publication task,
            # then we must Falsify the other one (if it exists)
            if task.is_publication and task.item:
                (self.get_queryset()
                 .filter(item=task.item)
                 .exclude(id=task.id)
                 .update(is_publication=False))

        diff = diff_tracker.get_diff(task)

        # If some user has been added to the assignees, notify them
        assignees_after = set(task.assignees.all())
        new_assignees = assignees_after - assignees_before
        if new_assignees:
            notify_when_assigned_to_task(self.request.user, task, new_assignees)
        if assignees_before:
            notify_when_my_task_updated(self.request.user, task, assignees_before, diff)

        activity_kwargs = dict(
            actor=self.request.user,
            desk=self.request.desk,
            target=task.get_linked_object(),
            action_object=task
        )
        if is_done_after and not is_done_before:
            activity_kwargs['verb'] = Activity.VERB_TASK_DONE
        else:
            activity_kwargs['verb'] = Activity.VERB_TASK_UPDATED
            activity_kwargs['diff'] = diff

        create_activity(**activity_kwargs)

        return task

    def destroy(self, request, *args, **kwargs):
        """
        We don't actually destroy the instance, but set its "hidden" flag to True
        """
        task = self.get_object()
        if not task.can_be_hidden:
            return HttpResponseForbidden("This task cannot be deleted")

        task.hide(user=self.request.user)

        create_activity(
            actor=self.request.user,
            desk=self.request.desk,
            verb=Activity.VERB_TASK_DELETED,
            target=task.get_linked_object(),
            action_object=task
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    def linked_tasks_response(self, linked_object):
        # Take the easy and not-robust path.
        # Only Item and Project are linked to some Tasks,
        # and they both do it through a M2M named 'tasks'.
        # Let's consider we'll continue to keep it simple in the future,
        # and just access the "tasks" attribute".
        tasks = linked_object.tasks

        queryset = (
            tasks.order_by('order')
            # VERY IMPORTANT : Filter the reminders to keep only those of the current user
            # ALso optimize by prefeteching the M2M relationship.
            .prefetch_related(Prefetch('reminders', queryset=Reminder.objects.filter(user=self.request.user)))
        )
        serializer = LinkedTaskSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, url_path='linked/(?P<content_type_id>\d+)/(?P<object_id>\d+)')
    def linked(self, request, *args, **kwargs):
        """
        List of the tasks linked to a generic object

        The target object is looked up by the two parameters in the url :
         * content_type_id : The id of the content_type
         * object_id : The id of the object of this content_type
        """
        return self.linked_tasks_response(self.get_generic_object())

    @action(detail=False, methods=['GET'], cross_desk=False)
    def done(self, request, *args, **kwargs):
        """
        All done tasks for current user
        """
        self.base_queryset = (Task.objects
                              .filter(assignees=self.request.user, done=True)
                              .order_by('deadline'))
        return self.list(request, *args, **kwargs)

    @action(detail=False, methods=['GET'], cross_desk=False)
    def undone(self, request, *args, **kwargs):
        """
        All undone tasks for current user
        """
        self.base_queryset = (Task.objects
                              .filter(assignees=self.request.user, done=False)
                              .order_by('deadline'))
        return self.list(request, *args, **kwargs)

    @action(detail=False, methods=['POST'])
    def set_order(self, request, *args, **kwargs):
        ids = []
        with transaction.atomic():
            queryset = self.get_queryset()
            for task_order in request.data:
                ids.append(task_order['id'])
                queryset.filter(id=task_order['id']).update(order=task_order['order'])

        queryset = queryset.filter(id__in=ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def send_notifications(self, request, *args, **kwargs):
        # The Task may have been hidden, don't user the standard manager for lookup
        task = get_object_or_404(Task.all_the_objects, pk=kwargs['pk'])
        type = self.request.data.get('type')

        if type == 'todo':
            notify_when_task_todo(self.request.user, task)
        elif type == 'deleted':
            notify_when_task_deleted(self.request.user, task)
        else:
            return HttpResponseBadRequest("type should be 'todo' or 'deleted'")

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['POST'])
    def import_task_group(self, request, *args, **kwargs):
        """
        Import a task group onto a target (generic) object.

        The target object is looked up by the two parameters in the post data :
         * content_type_id : The id of the content_type
         * object_id : The id of the object of this content_type
        """
        linked_object = self.get_generic_object()
        try:
            import_task_group_on_instance(
                linked_object=linked_object,
                task_group_id=self.request.data.get('task_group_id'),
                user=request.user
            )
        except TaskGroup.DoesNotExist:
            return HttpResponseBadRequest()

        return self.linked_tasks_response(linked_object)


class TaskTemplateViewSet(viewsets.ModelViewSet):
    """
    A Task template is a task managed in a TaskGroup,
    intended to be copied to an actual Task attached to an Item.

    Only admins can manage the Task templates
    """
    serializer_class = TaskTemplateSerializer
    permission_classes = [
        api_utils.DeskPermission,
        api_utils.IsAdminOrReadOnlyPermission
    ]

    def get_queryset(self):
        return Task.objects.filter(
            desk=self.request.desk,
            task_group__desk=self.request.desk
        ).exclude(
            # Limit access to tasks templates through this ViewSet
            task_group=None
        )

    def perform_create(self, serializer):
        return serializer.save(
            desk=self.request.desk,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        with transaction.atomic():
            task_template = serializer.save(updated_by=self.request.user)
            # If the task template has been defined as the publication task,
            # then we must Falsify the other one (if it exists)
            if task_template.is_publication:
                (self.get_queryset()
                 .filter(task_group=task_template.task_group)
                 .exclude(id=task_template.id)
                 .update(is_publication=False))

    def perform_destroy(self, task):
        with transaction.atomic():
            # Update other tasks order
            (self.get_queryset()
                .filter(order__gt=task.order)
                .update(order=Field('order')-1))
            # Delete the task
            task.delete()

    @action(detail=False, methods=['POST'])
    def set_order(self, request, *args, **kwargs):
        ids = []
        with transaction.atomic():
            queryset = self.get_queryset()
            for task_order in request.data:
                ids.append(task_order['id'])
                queryset.filter(id=task_order['id']).update(order=task_order['order'])

        queryset = queryset.filter(id__in=ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TaskGroupViewSet(viewsets.ModelViewSet):
    """
    A Task template is a task managed in a TaskGroup,
    intended to be copied to an actual Task attached to an Item.

    Only admins can manage the Task templates
    """
    serializer_class = TaskGroupSerializer
    permission_classes = [
        api_utils.DeskPermission,
        api_utils.IsAdminOrReadOnlyPermission
    ]

    def get_queryset(self):
        return TaskGroup.objects.filter(
            desk=self.request.desk,
        ).order_by('name')

    def perform_create(self, serializer):
        return serializer.save(
            desk=self.request.desk,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, task_group):
        # Delete the task_group. Linked Task templates will be deleted on cascade.
        task_group.delete()
