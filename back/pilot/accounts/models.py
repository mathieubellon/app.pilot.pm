from django.utils.translation import ugettext_lazy as _
from django.db import models

NO_USAGE_LIMIT = -1
TRIAL_PLAN_ID = "TRIAL"


class UsageLimitsModelMixin(models.Model):
    """
    Base class inherited by SubscriptionPlan and Desk which define limits that can apply on an account.

    The standard limits are defined by a SubscriptionPlan instance.
    Desk instances are linked to a SubscriptionPlan, and have the limit from the subscription plan.
    But Desk instances can also overrides any limit, in which case the value defined on the desk takes precedence.
    An override on the desk is defined by a non-null value.

    Each limit field can have three state :
    1/ A positive integer value to set the limit
    2/ The NO_USAGE_LIMIT constant to disable limit checking
    3/ None, only on the Desk object
    """
    max_users = models.IntegerField(
        verbose_name=_("Nombre maximum d'utilisateurs"),
        null=True,
        blank=True
    )

    max_projects = models.IntegerField(
        verbose_name=_("Nombre maximum de projets"),
        null=True,
        blank=True
    )

    max_items = models.IntegerField(
        verbose_name=_("Nombre maximum de contenus"),
        null=True,
        blank=True
    )

    max_assets_storage = models.IntegerField(
        verbose_name=_("Taille de stockage maximale (en Giga-octets)"),
        null=True,
        blank=True
    )

    # We need the null part of the NullBooleanField
    # so the desk can define "I dont want to override the default"
    advanced_features = models.NullBooleanField(
        verbose_name=_("Accès aux fonctionnalités avancées ?"),
    )

    class Meta:
        abstract = True


class SubscriptionPlan(UsageLimitsModelMixin, models.Model):
    name = models.CharField(
        verbose_name=_("Nom"),
        max_length=200
    )

    display_price = models.CharField(
        max_length=100,
        verbose_name=_("Prix affiché"),
        help_text=_("Valeur d'affichage uniquement, aucun impact sur la facturation réelle."
                    "Seule la configuration Stripe impacte la prix facturé."),
        blank=True
    )

    stripe_plan_id = models.CharField(
        verbose_name=_("Stripe plan id"),
        max_length=50
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name

    @staticmethod
    def get_trial_subscription():
        return SubscriptionPlan.objects.get(stripe_plan_id=TRIAL_PLAN_ID)