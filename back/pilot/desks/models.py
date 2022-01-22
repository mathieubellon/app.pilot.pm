from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres import fields as pg_fields

from pilot.accounts.models import SubscriptionPlan, UsageLimitsModelMixin
from pilot.organizations.models import Organization
from pilot.utils import pilot_languages
from pilot.utils.models import ChangeTrackingModel


def default_languages():
    return ['en_US']


def language_list_validator(value):
    """
    Check that value is a list or None and that all items belong to pilot_languages.LANGUAGES keys
    """
    ERROR_MESSAGE = "Validation error, this field expects a list of language codes"
    if value is None:
        return

    if not isinstance(value, list):
        raise ValidationError(ERROR_MESSAGE)

    if any(lang not in pilot_languages.LANGUAGES.keys() for lang in value):
        raise ValidationError(ERROR_MESSAGE)


class Desk(UsageLimitsModelMixin, ChangeTrackingModel):
    """A desk."""

    name = models.CharField(
        verbose_name=_("Nom"),
        max_length=200
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        verbose_name=_("Organisation"),
        related_name='desks'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Actif"),
        help_text=_("Un desk non actif n'est plus utilisable, les utilisateurs ne peuvent plus s'y connecter")
    )

    logo = models.ImageField(
        upload_to='logos',
        verbose_name=_("Logo"),
        blank=True,
        null=True
    )

    # -----------
    # Config
    # -----------

    item_languages_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Langues de contenus activées"),
        help_text=_("Indique si les utilisateurs du desk peuvent flagguer les contenus avec une langue")
    )

    allowed_languages = pg_fields.ArrayField(
        base_field=models.TextField(),
        null=True,
        blank=True,
        default=default_languages,
        verbose_name=_("Langues autorisées pour marquer les contenus"),
        help_text=_("Code langue sous la forme 'fr_FR'. Le premier code est la langue par défaut."),
        validators=[language_list_validator]
    )

    private_items_enabled = models.BooleanField(
        default=True,
        verbose_name=_("Items privés activés"),
        help_text=_("Indique si les utilisateurs du desk peuvent rendre un item privé")
    )

    creation_forms_fields_visibles_by_default = models.BooleanField(
        default=False,
        verbose_name=_("Afficher par défaut tous les champs des formulaires de créations"),
    )

    # -----------
    # Subscription data
    # -----------

    subscription_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
        verbose_name=_("Type d'abonnement"),
        related_name='desks'
    )

    display_price = models.CharField(
        max_length=100,
        verbose_name=_("Prix affiché"),
        help_text=_("Pour les orga facturée en manuel, le prix affiché à l'admin du compte."
                    "Valeur d'affichage uniquement, aucun impact sur la facturation réelle."),
        blank=True
    )

    subscription_terminated = models.BooleanField(
        default=False,
        verbose_name=_("Abonnement arrêté"),
        help_text=_("Indique si l'utilisateur a demandé la fin de son abonnement")
    )

    class Meta:
        verbose_name = _('Desk')
        verbose_name_plural = _('Desks')
        ordering = ['name']

    def __str__(self):
        return self.name

    def build_choices_from_allowed_languages(self, empty_value=''):
        """
        Return a tuple suitable for a choice form field. The `empty_value` kwarg is to customize the list
        for filtering purposes.
        """
        if not self.allowed_languages or not self.item_languages_enabled:
            return []
        choices = [(empty_value, _("Aucun"))]
        choices += [(lang_code, pilot_languages.LANGUAGES[lang_code]) for lang_code in self.allowed_languages]
        return choices

    def save(self, *args, **kwargs):
        is_creation = not self.pk

        super(Desk, self).save(*args, **kwargs)

        # On creation, init some data after the creation
        if is_creation:
            from pilot.labels.initial_labels import init_labels_for_desk
            from pilot.item_types.initial_item_types import init_item_types_for_desk
            from pilot.tasks.initial_tasks import init_default_task_group_for_desk
            from pilot.workflow.initial_states import init_workflow_states_for_desk
            from pilot.wiki.initial_wiki import init_default_wiki_home_page_for_desk

            init_labels_for_desk(self)
            init_item_types_for_desk(self)
            init_default_task_group_for_desk(self)
            init_workflow_states_for_desk(self)
            init_default_wiki_home_page_for_desk(self)

    def get_logo_url(self):
        # Don't call self.logo.url, because this would load the entire boto s3 ecosystem,
        # and bloat the memory, which we don't need
        return f"{settings.AWS_S3_BASE_URL}{self.logo}"
