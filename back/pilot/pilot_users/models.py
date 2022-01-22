import datetime

import uuid
from io import BytesIO
from PIL import Image
import re

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.contrib.auth.tokens import default_token_generator
from django.contrib.postgres import fields as pg_fields
from django.core import validators
from django.core.files.base import ContentFile
from django.urls import reverse
from django.db import models
from django.utils import timezone as dj_timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlquote, urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField

from pilot.accounts.usage_limit import UserUsageLimit
from pilot.desks.models import Desk
from pilot.main.menu import Menu, LOGIN_MENU_CHOICES
from pilot.organizations.models import Organization
from pilot.pilot_users.identicons import Identicon
from pilot.utils import pilot_languages, pilot_timezones
from pilot.utils.models import ChangeTrackingModel
from pilot.utils.token_generator import generate_token

# Permission name definitions.
PERMISSION_ADMINS = 'Administrators'
PERMISSION_EDITORS = 'Editors'
PERMISSION_RESTRICTED_EDITORS = 'Restricted Editors'
DEFAULT_AVATAR = 'https://pilotapp-production-master.s3.amazonaws.com/avatars/None.png'

PILOT_PERMISSION_CHOICES = (
    (PERMISSION_ADMINS, _("Administrateur")),
    (PERMISSION_EDITORS, _("Éditeur")),
    (PERMISSION_RESTRICTED_EDITORS, _("Éditeur restreint")),
)

slug_name_validator = validators.RegexValidator(
    re.compile('^[a-zA-Z0-9_]+$'),
    _("Le nom ne peut contenir que des lettres sans accent, chiffres et \"_\""),
    'invalid'
)


def get_default_notification_preferences():
    from pilot.notifications.const import NotificationPreference
    return {
        NotificationPreference.MENTION: {'email': True, 'app': True},
        NotificationPreference.REMINDER: {'email': True, 'app': True},
        NotificationPreference.SHARING: {'email': True, 'app': True},
        NotificationPreference.TASK: {'email': True, 'app': True},
    }


class UserPermissions(object):
    def __init__(self, permission, is_organization_admin):
        self.permission = permission
        self.is_organization_admin = is_organization_admin

    @property
    def is_admin(self):
        return self.permission == PERMISSION_ADMINS

    @property
    def is_editor(self):
        return self.permission == PERMISSION_EDITORS

    @property
    def is_restricted_editor(self):
        return self.permission == PERMISSION_RESTRICTED_EDITORS

    def __repr__(self):
        return "<UserPermissions: permission={} is_organization_admin={}".format(self.permission, self.is_organization_admin)


class Team(ChangeTrackingModel):
    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='teams'
    )

    name = models.CharField(
        verbose_name=_("Nom d'équipe"),
        max_length=160,
        help_text=_("160 caractères maximum. Lettres, nombre et \"_\" ."),
        validators=[slug_name_validator],
        db_index=True
    )

    description = models.TextField(
        verbose_name=_("Description"),
        blank=True
    )

    class Meta:
        verbose_name = _('Equipe')
        verbose_name_plural = _('Equipes')
        ordering = ['name']
        # We need each team to have a unique name across a desk to reference it through @mention
        unique_together = ['desk', 'name']

    def __str__(self):
        return self.name


class PilotUser(AbstractBaseUser):
    """
    A Pilot user.
    Custom Django User model: https://docs.djangoproject.com/en/1.5/topics/auth/customizing/#auth-custom-user
    """

    AVATAR_SIZE = (256, 256)

    avatar_changed = False

    organizations = models.ManyToManyField(
        Organization,
        verbose_name=_("Organizations"),
        related_name='users',
        through='UserInOrganization'
    )

    desks = models.ManyToManyField(
        Desk,
        verbose_name=_("Desks"),
        related_name='users',
        through='UserInDesk'
    )

    teams = models.ManyToManyField(
        Team,
        verbose_name=_("Equipes"),
        related_name='users'
    )

    # Desks in which this user were active at a past time,
    # but has been removed.
    # We keep a link here so the admin can make a quick reactivation
    desks_deactivated = models.ManyToManyField(
        Desk,
        verbose_name=_("Desks"),
        related_name='users_deactivated',
        through='UserInDeskDeactivated'
    )

    first_name = models.CharField(
        verbose_name=_("Prénom"),
        max_length=80,
        blank=True
    )

    last_name = models.CharField(
        verbose_name=_("Nom"),
        max_length=80,
        blank=True
    )

    email = models.EmailField(
        verbose_name=_("Adresse email"),
        max_length=254,
        unique=True
    )

    username = models.CharField(
        verbose_name=_("Nom d'utilisateur"),
        max_length=160,
        unique=True,
        help_text=_("160 caractères maximum. Lettres, nombre et \"_\" ."),
        validators=[slug_name_validator],
        db_index=True
    )

    language = models.CharField(
        verbose_name=_("Langue de l'interface"),
        max_length=2,
        choices=pilot_languages.PILOT_UI_LANGUAGES,
        default=pilot_languages.FR_LANG
    )

    timezone = models.CharField(
        verbose_name=_("Fuseau horaire"),
        max_length=50,
        choices=pilot_timezones.PILOT_TIMEZONE_CHOICES,
        default=pilot_timezones.DEFAULT_TIMEZONE
    )

    avatar = models.ImageField(
        upload_to='avatars',
        verbose_name=_("Avatar"),
        blank=True,
        null=True
    )

    is_superuser = models.BooleanField(
        _('superuser status'),
        default=False,
        help_text=_(
            'Designates that this user has all permissions without '
            'explicitly assigning them.'
        ),
    )

    is_staff = models.BooleanField(
        verbose_name=_("Fait partie du staff"),
        default=False,
        help_text=_("Indique si l'utilisateur peut se connecter à l'interface d'administration")
    )

    wiped = models.BooleanField(
        verbose_name=_("Wiped"),
        default=False,
        help_text=_("Indique si l'utilisateur a subit un wipeout (suppression de ses données)")
    )

    date_joined = models.DateTimeField(
        verbose_name=_("Date d'inscription"),
        default=dj_timezone.now
    )

    cgv_acceptance_date = models.DateTimeField(
        verbose_name=_("Acceptation CGV"),
        null=True,
        blank=True,
        help_text=_("Date/heure de clic sur la checkbox d'acceptation des CGV")
    )

    login_menu = models.CharField(
        verbose_name=_("Menu de connexion"),
        max_length=100,
        choices=LOGIN_MENU_CHOICES,
        default=Menu.PROJECTS.name,
        null=False,
        blank=False,
    )

    # A dict of preferences for notifications by email :
    # { 'mention': True, 'review': False ... }
    notification_preferences = pg_fields.JSONField(
        verbose_name=_("Notification preferences"),
        default=get_default_notification_preferences
    )

    phone = models.CharField(
        verbose_name=_("Téléphone"),
        max_length=20,
        blank=True
    )

    localization = models.CharField(
        verbose_name=_("Localisation"),
        max_length=254,
        blank=True
    )

    job = models.CharField(
        verbose_name=_("Métier"),
        max_length=254,
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['username']

    def __str__(self):
        return self.get_short_name()

    def save(self, *args, **kwargs):
        # self.avatar_changed has to be set in form cleanup
        if self.avatar and self.avatar_changed:
            img = Image.open(self.avatar)
            img.thumbnail(self.AVATAR_SIZE, Image.ANTIALIAS)
            self._update_avatar(img)

        # Without provided avatar, an identicon is created
        if not self.avatar:  # update
            self._make_identicon()

        super(PilotUser, self).save(*args, **kwargs)

    # All authenticated request.user will get initialized with a desk connection
    # by the PilotMiddleware
    user_in_organization = None
    user_in_desk = None
    def set_desk_connection(self, user_in_organization, user_in_desk):
        self.user_in_organization = user_in_organization
        self.user_in_desk = user_in_desk
        self.set_permissions(user_in_desk.permission, user_in_organization.is_organization_admin)

    _permissions = None
    def set_permissions(self, permission, is_organization_admin):
        self._permissions = UserPermissions(permission, is_organization_admin)

    @property
    def permissions(self):
        if self._permissions is None:
            raise Exception("Permissions must be set for the current desk before calling user.permissions")

        return self._permissions

    def get_full_name(self):
        """Returns the first_name plus the last_name, with a space in between."""
        return '{0} {1}'.format(self.first_name, self.last_name).strip()

    def get_short_name(self):
        """Returns the short name for this user."""
        return '@{0}'.format(self.username)

    def get_friendly_name(self):
        """Returns either the full name if available, else fallback on the short name"""
        full_name = self.get_full_name()
        return full_name if full_name else self.get_short_name()

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)

    def get_avatar_url(self):
        """
        In production, return the user avatar as is.

        In development, we want to avoid 404 responses when fetching inexistent avatar links on S3.
        Instead of using an actual S3 link, we generate an avatar for each user, seeded with its email,
        and send it encoded as base64 data type.
        """
        if settings.DEBUG:
            identicon = Identicon(self.email, background="#f0f0f0")
            # Convert the base64 bytes to a string
            return f"data:image/png;base64,{identicon.base64().decode()}"

        if self.avatar:
            # Don't call self.avatar.url, because this would load the entire boto s3 ecosystem,
            # and bloat the memory, which we don't need
            return f"{settings.AWS_S3_BASE_URL}{self.avatar}"

        return DEFAULT_AVATAR

    def get_token_url(self, url_name):
        """Generates a one-use only link."""
        return reverse(url_name, kwargs={
            'uidb64': urlsafe_base64_encode(force_bytes(self.id)),
            'token': default_token_generator.make_token(self),
        })

    def get_undone_tasks_count(self, desk):
        return self.tasks.filter(desk=desk, done=False).count()

    def get_unread_notifications_count(self, desk):
        return self.notifications_received.filter(desk=desk, is_read=False).count()

    def _update_avatar(self, img):
        # Generate a random uuid for the file name path, to avoid guessing by desk id
        filename = '{0}.png'.format(uuid.uuid4())
        fp = BytesIO()
        img.save(fp, "PNG")
        cf = ContentFile(fp.getvalue())
        self.avatar.save(name=filename, content=cf, save=False)
        self.avatar_changed = False

    def _make_identicon(self):
        identicon = Identicon(self.email, background="#f0f0f0")
        identicon.calculate()
        img = identicon.image
        self._update_avatar(img)

    def has_perm(self, perm, obj=None):
        """Check cockpit authorizations"""
        return self.is_superuser

    def has_module_perms(self, app_label):
        """Check cockpit authorizations"""
        return self.is_superuser

    def wipeout(self):
        if self.desks.exists():
            raise Exception(f"Cannot wipeout user {self.id} because he's still active in a desk")

        self.email = f'UserDeleted{self.id}@pilot.pm'
        self.username = f'UserDeleted{self.id}'
        self.wiped = True

        self.first_name = ''
        self.last_name = ''
        self.phone = ''
        self.localization = ''
        self.job = ''
        self.avatar = None
        self.notification_preferences = {}
        self.last_login = None
        self.cgv_acceptance_date = None
        self.date_joined = datetime.datetime(2000, 1, 1)

        # Bypass the avatar checks on self.save
        super(PilotUser, self).save()

        self.teams.clear()
        self.desks_deactivated.clear()


class UserInOrganization(models.Model):
    # The two M2M Through fields
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='user_in_organization_set'
    )
    user = models.ForeignKey(
        PilotUser,
        on_delete=models.CASCADE,
        related_name='user_in_organization_set'
    )

    is_organization_admin = models.BooleanField(
        verbose_name=_("Administre l'organisation"),
        default=False,
        help_text=_("Indique si l'utilisateur peut accéder à l'écran de gestion de facturation de l'organisation")
    )

    class Meta:
        db_table = 'organizations_organization_users'  # Historic name before the through table


class UserInDesk(models.Model):
    # The two M2M Through fields
    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        related_name='user_in_desk_set'
    )
    user = models.ForeignKey(
        PilotUser,
        on_delete=models.CASCADE,
        related_name='user_in_desk_set'
    )

    permission = models.CharField(
        max_length=100,
        verbose_name=_("Permission"),
        choices=PILOT_PERMISSION_CHOICES,
    )

    # Use a column of JsonType to store user config data
    # We prefer one json column for a specific set of data
    # Always prepend with "config_"

    # The tiles added by the user, in the format
    # [ { name: 'tileName', params: {...} }, ... ]
    config_dashboard = JSONField(
        default=dict,
        blank=True
    )

    config_calendar = JSONField(
        default=dict,
        blank=True
    )

    class Meta:
        db_table = 'desks_desk_users'  # Historic name before the through table


class UserInDeskDeactivated(models.Model):
    # The two M2M Through fields
    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        related_name='user_in_desk_deactivated_set'
    )
    user = models.ForeignKey(
        PilotUser,
        on_delete=models.CASCADE,
        related_name='user_in_desk_deactivated_set'
    )

    permission = models.CharField(
        max_length=100,
        verbose_name=_("Permission"),
        choices=PILOT_PERMISSION_CHOICES,
    )

    config_dashboard = JSONField(
        default=dict,
        blank=True
    )

    config_calendar = JSONField(
        default=dict,
        blank=True
    )


class InvitationToken(ChangeTrackingModel):
    """An invitation token used for the creation of a user account."""

    email = models.EmailField(
        verbose_name=_("E-mail")
    )

    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='invitation_tokens',
    )

    permission = models.CharField(
        verbose_name=_("Permission"),
        choices=PILOT_PERMISSION_CHOICES,
        max_length=36,
        default=PERMISSION_RESTRICTED_EDITORS
    )

    teams = models.ManyToManyField(
        Team,
        verbose_name=_("Equipes"),
        blank=True
    )

    token = models.CharField(
        verbose_name=_("Token"),
        max_length=255
    )

    # The link between the token and the user will be made once the token has been validated
    # so that the token will be deleted along with the user object if the need arises.
    user = models.ForeignKey(
        PilotUser,
        on_delete=models.CASCADE,
        verbose_name=_("Utilisateur"),
        null=True,
        blank=True
    )

    used_at = models.DateTimeField(
        verbose_name=_("Utilisé le"),
        blank=True,
        null=True
    )

    used = models.BooleanField(
        verbose_name=_("Utilisé"),
        default=False
    )

    class Meta:
        verbose_name = _("Invitation token")
        verbose_name_plural = _("Invitation tokens")
        unique_together = ('desk', 'token')

    def __str__(self):
        return _("{0} pour le desk #{1}").format(self.token, self.desk_id)

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.pk:
            UserUsageLimit(self.desk).check_limit()

        if not self.token:
            self.token = generate_token()

        # Ensure that token fields are unique together.
        while InvitationToken.objects. \
                filter(token=self.token). \
                exclude(pk=self.pk). \
                exists():
            self.token = generate_token()

        # Ensure email is stored as lowercase
        self.email = self.email.lower()

        super(InvitationToken, self).save(*args, **kwargs)
