from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres import fields as pg_fields
from picklefield.fields import PickledObjectField

from pilot.desks.models import Desk
from pilot.queue.jobs_registar import JOB_TYPE_CHOICES, get_job_by_type
from pilot.utils.models import CreateTrackingModel


class JobTracker(CreateTrackingModel, models.Model):
    """
    Track a job handled by RQ
    """

    STATE_QUEUED = 'queued'
    STATE_STARTED = 'started'
    STATE_FINISHED = 'finished'
    STATE_FAILED = 'failed'
    STATE_REDIS_DOWN = 'redis_down'
    STATE_ZOMBIE = 'zombie'

    STATES_CHOICES = (
        (STATE_QUEUED, _("En cours")),
        (STATE_STARTED, _("Démarré")),
        (STATE_FINISHED, _("Terminé")),
        (STATE_FAILED, _("Erreur")),
        (STATE_REDIS_DOWN, _("Impossible de lancer la tâche")),
        (STATE_ZOMBIE, _("Zombie")),
    )

    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='exports'
    )

    job_id = models.CharField(
        verbose_name=_("UUID utilisé par RQ"),
        max_length=100
    )

    job_type = models.CharField(
        verbose_name=_("Type de job"),
        max_length=30,
        choices=JOB_TYPE_CHOICES
    )

    state = models.CharField(
        verbose_name=_("Etat"),
        max_length=30,
        choices=STATES_CHOICES,
        default=STATE_QUEUED
    )

    try_count = models.PositiveSmallIntegerField(
        verbose_name=_("Nombre d'essai"),
        default=1
    )

    finished_at = models.DateTimeField(
        verbose_name=_("Términé à"),
        blank=True,
        null=True
    )

    # Job's args pickled
    args = PickledObjectField(
        blank=True,
        null=True
    )

    # Job's kwargs pickled
    kwargs = PickledObjectField(
        blank=True,
        null=True
    )

    # Job's timeout
    timeout = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    # Additionnal arbitrary data the job wish to store in the db.
    # Don't use it to pass kwargs to the job, rq can do this already.
    data = pg_fields.JSONField(
        verbose_name=_("Data"),
        blank=True,
        default=dict
    )

    def __str__(self):
        return "<JobTracker id={} job_id={}>".format(self.id, self.job_id)

    @property
    def in_progress(self):
        return self.state in (JobTracker.STATE_QUEUED, JobTracker.STATE_STARTED)

    def requeue(self):
        if self.state not in (JobTracker.STATE_FAILED, JobTracker.STATE_ZOMBIE):
            raise Exception("Only failed or zombie jobs can be requed")

        job_class = get_job_by_type(self.job_type)
        job_class.enqueue_job(
            args=self.args,
            kwargs=self.kwargs,
            job_id=self.job_id,
            timeout=self.timeout
        )

        # Reset creation date to prevent the jobs monitoring to set it as a zombie immediatly
        self.created_at = timezone.now()
        self.state = self.STATE_QUEUED
        self.save()


