from django.forms.models import model_to_dict
from django.utils.translation import ugettext_lazy as _

from pilot.items.models import Item
from pilot.tasks.models import Task, TaskGroup

INITIAL_TASKS = (
    dict(
        name=_("Publier"),
        order=0,
        show_in_publishing_calendar=True,
        can_be_hidden=False,
        is_publication=True
    ),
)


def init_default_task_group_for_desk(desk):
    """
    When a desk is created, init its default TaskGroup
    """
    task_group = TaskGroup.objects.create(desk=desk, created_by_id=1, name='Défaut')
    for dict_state in INITIAL_TASKS:
        task_group.tasks.create(desk=desk, created_by_id=1, **dict_state)


def import_task_group_on_instance(linked_object, task_group_id, user, publication_dt=None):
    """
    Import the task templates of a task group onto an item or project.

    If there's a publication task in the task template, it may either :
     - Be negated  ( because there's already another one on the item )
     - Or get the publication_dt assigned to its deadline
    """
    task_group = TaskGroup.objects.prefetch_related('tasks').get(
        id=task_group_id,
        desk=linked_object.desk
    )
    # No need to use tasks.count(), because we'll fetch tasks.all() anyway
    existing_tasks_count = len(linked_object.tasks.all())
    for task_template in task_group.tasks.all():
        model_data = model_to_dict(task_template, exclude=['id', 'task_group', 'created_at', 'updated_by'])
        model_data['desk'] = linked_object.desk
        model_data['created_by'] = user
        # Import at the end of the existing tasks
        model_data['order'] += existing_tasks_count
        assignees = model_data.pop('assignees')
        if task_template.is_publication and isinstance(linked_object, Item):
            # If there's already a publication task, we must negate the is-publication flag of this task template
            if bool(linked_object.publication_task):
                model_data['is_publication'] = False
            # Else, there's no publication task yet, we can assign it the publication_dt
            else:
                model_data['deadline'] = publication_dt

        task = Task(**model_data)
        # Prevent SavecFilterImpactor to trigger, to avoid a cascade of jobs in the queue
        task.impact_saved_filter = False
        task.save()
        task.assignees.set(assignees)
        linked_object.tasks.add(task)


def init_publication_task_for_item(item, publication_dt):
    Task.objects.create(
        desk=item.desk,
        name=_("Publier"),
        deadline=publication_dt,
        order=0,
        show_in_publishing_calendar=True,
        is_publication=True,
        item=item
    )
