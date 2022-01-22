from django.db import models
from django.utils.translation import ugettext_lazy as _

from pilot.utils.models import ChangeTrackingModel


class Organization(ChangeTrackingModel):
    """An organization."""

    name = models.CharField(
        verbose_name=_("Nom"),
        max_length=200
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Actif"),
        help_text=_("Une organisation non active n'est plus utilisable, les utilisateurs ne peuvent plus s'y connecter")
    )

    max_desks = models.PositiveSmallIntegerField(
        verbose_name=_("Nombre maximum de desks"),
        default=1
    )

    # -----------
    # Billing data
    # -----------

    billing_name = models.CharField(
        verbose_name=_("Nom de facturation"),
        max_length=200
    )

    billing_address = models.CharField(
        verbose_name=_("Adresse de facturation"),
        max_length=500,
        blank=True
    )

    billing_postal_code = models.CharField(
        verbose_name=_("Code postal de facturation"),
        max_length=10,
        blank=True
    )

    billing_city = models.CharField(
        verbose_name=_("Ville de facturation"),
        max_length=200,
        blank=True
    )

    billing_vat = models.CharField(
        verbose_name=_("N° de TVA"),
        max_length=50,
        blank=True
    )

    # -----------
    # Subscription data
    # -----------

    manual_billing = models.BooleanField(
        default=False,
        verbose_name=_("Facturation manuelle"),
        help_text=_("Indique si cette organisation est facturée manuellement (pas de stripe auto)")
    )

    stripe_customer_id = models.CharField(
        verbose_name=_("Stripe customer id"),
        max_length=50,
        blank=True
    )

    stripe_subscription_id = models.CharField(
        verbose_name=_("Stripe subscription id"),
        max_length=50,
        blank=True
    )

    cgv_acceptance_date = models.DateTimeField(
        verbose_name=_("Acceptation CGV"),
        null=True,
        blank=True,
        help_text=_("Date/heure de clic sur la checkbox d'acceptation des CGV")
    )

    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')

    def __str__(self):
        return self.name
