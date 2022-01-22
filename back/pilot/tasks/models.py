from django.db import models
from django.utils.translation import ugettext_lazy as _

from pilot.channels.models import Channel
from pilot.desks.models import Desk
from pilot.items.models import Item
from pilot.notifications.jobs import SavedFilterImpactorModel
from pilot.notifications.reminders import ReminderImpactorModel
from pilot.pilot_users.models import PilotUser
from pilot.projects.models import Project
from pilot.utils.models import ChangeTrackingModel, HideableModel, OptionalCreatorChangeTrackingModel, \
    NaiveDateTimeField


class TasksManager(models.Manager):
    def get_queryset(self):
        """Only visible Tasks."""
        return (super(TasksManager, self).get_queryset()
            .filter(hidden=False)
            # Hide tasks for trashed or hidden items
            .exclude(item__in_trash=True)
            .exclude(item__hidden=True)
        )


class TaskGroup(ChangeTrackingModel):
    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='task_groups'
    )

    name = models.CharField(
        verbose_name=_("Nom"),
        max_length=200
    )

    description = models.CharField(
        verbose_name=_("Description"),
        max_length=500,
        blank=True
    )


class Task(OptionalCreatorChangeTrackingModel,
           HideableModel,
           # Task deadline/is_publication updates may trigger modifications on the SavedFilter
           # which are filtering against item.publication_dt
           SavedFilterImpactorModel,
           ReminderImpactorModel):

    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='tasks'
    )

    name = models.TextField(
        verbose_name=_("Nom"),
        blank=True
    )

    assignees = models.ManyToManyField(
        PilotUser,
        verbose_name=_("Responsables"),
        related_name='tasks',
        blank=True
    )

    deadline = NaiveDateTimeField(
        verbose_name=_("Echeance"),
        blank=True,
        null=True
    )

    done = models.BooleanField(
        verbose_name=_("Effectué"),
        default=False
    )

    done_by = models.ForeignKey(
        PilotUser,
        on_delete=models.CASCADE,
        verbose_name=_("Effectué par"),
        related_name='%(class)s_done',
        null=True,
        blank=True
    )

    done_at = models.DateTimeField(
        verbose_name=_("Effectué à"),
        null=True,
        blank=True
    )

    # Tasks can be linked to only a single other object.
    # We put the order field directly on the task object,
    # to simplify the ordering of the tasks
    order = models.PositiveSmallIntegerField(
        verbose_name=_("Ordre"),
    )

    show_in_publishing_calendar = models.BooleanField(
        verbose_name=_("Apparait dans le calendrier de publication"),
        default=False
    )

    # If the task is allowed to be hidden
    can_be_hidden = models.BooleanField(
        verbose_name=_("Peut être supprimée"),
        default=True
    )

    # Flag the publication task
    is_publication = models.BooleanField(
        verbose_name=_("Publication"),
        default=False
    )

    # We can link the task either to an item or to a project or to a channel
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        verbose_name=_("Contenu"),
        related_name='tasks',
        null=True,
        blank=True
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        verbose_name=_("Projet"),
        related_name='tasks',
        null=True,
        blank=True
    )

    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        verbose_name=_("Channel"),
        related_name='tasks',
        null=True,
        blank=True
    )

    # For Task templates
    task_group = models.ForeignKey(
        TaskGroup,
        on_delete=models.CASCADE,
        verbose_name=_("Groupe de tâche"),
        related_name='tasks',
        null=True,
        blank=True
    )

    objects = TasksManager()
    all_the_objects = models.Manager()  # for django admin

    class Meta:
        verbose_name = _('task')
        verbose_name_plural = _('tasks')
        ordering = ['order']

    def __str__(self):
        return self.name

    def get_linked_object(self):
        if self.project:
            return self.project
        elif self.item:
            return self.item
        elif self.channel:
            return self.channel

        return None

    def get_absolute_url(self):
        linked_object = self.get_linked_object()

        if self.hidden or not linked_object or linked_object.hidden:
            return None

        return f"{linked_object.get_absolute_url()}?showTask={self.id}"
