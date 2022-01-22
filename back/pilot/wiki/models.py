from django.contrib.postgres import fields as pg_fields
from django.db import models, transaction
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework.utils.encoders import JSONEncoder

from pilot.assets.models import Asset
from pilot.desks.models import Desk
from pilot.utils.models import ChangeTrackingModel, CreateTrackingModel, HideableModel


class WikiPageManager(models.Manager):
    def get_queryset(self):
        """Only visible WikiPage."""
        return super(WikiPageManager, self).get_queryset().filter(hidden=False)


class WikiPage(ChangeTrackingModel,
               HideableModel,
               models.Model):
    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='wiki_pages'
    )

    name = models.CharField(
        verbose_name=_("Nom"),
        max_length=500
    )

    # A rich-text field
    content = pg_fields.JSONField(
        verbose_name=_("Contenu"),
        encoder=JSONEncoder,
        default=dict,
        blank=True
    )

    is_home_page = models.BooleanField(
        verbose_name=_('Home Page'),
        default=False
    )

    assets = models.ManyToManyField(
        Asset,
        verbose_name=_("Fichiers liés"),
        related_name='wiki_pages',
        blank=True
    )

    objects = WikiPageManager()
    all_the_objects = models.Manager()  # for django admin

    class Meta:
        verbose_name = _("Page de wiki")
        verbose_name_plural = _("Pages de wiki")
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if self.hidden:
            return None

        if self.is_home_page:
            return reverse('ui_wiki_home_page')
        else:
            return reverse('ui_wiki_page', kwargs={'wiki_page_pk': self.pk})

    def save(self, *args, **kwargs):
        # Save the ItemType and its snapshot into a transaction to stay consistent
        with transaction.atomic():
            # Save the item type normally
            super(WikiPage, self).save(**kwargs)
            self.create_revision()

    def create_revision(self):
        # The creator of the revision is the last updater of the wiki page
        # If we create the first revision, there won't be any item updater, so use the creator
        creator = self.updated_by or self.created_by
        # Save the snapshot
        return WikiPageRevision.objects.create(
            wiki_page=self,
            created_by=creator,
            name=self.name,
            content=self.content
        )


class WikiPageRevision(CreateTrackingModel):
    wiki_page = models.ForeignKey(
        WikiPage,
        on_delete=models.SET_NULL,
        verbose_name=_("Page de  wiki"),
        related_name='revisions',
        null=True
    )

    name = models.CharField(
        verbose_name=_("Nom"),
        max_length=500
    )

    # A rich-text field
    content = pg_fields.JSONField(
        verbose_name=_("Contenu"),
        encoder=JSONEncoder,
        default=dict,
        blank=True
    )

    class Meta:
        verbose_name = _("Wiki page revision")
        verbose_name_plural = _("Wiki page revisions")
        ordering = ('-created_at',)
        get_latest_by = 'created_at'
