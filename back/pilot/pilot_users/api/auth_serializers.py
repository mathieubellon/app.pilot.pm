from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation
from django.contrib.auth import authenticate

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from pilot.desks.utils import get_current_desk
from pilot.pilot_users.models import PilotUser
from pilot.utils.api.serializers import EmailLowerCaseField

auth_error_messages = {
    'accept_terms': _('Veuillez accepter les CGU pour continuer'),
    'email_already_used': _("L'email \"{0}\" est déjà utilisé. Merci d'en choisir un autre."),
    'invalid_login': _("Ces informations de connexion ne sont pas reconnues."),
    'inactive': _("This account is inactive."),
    'password_incorrect': _("Your old password was entered incorrectly. Please enter it again."),
    'password_mismatch': _("The two password fields didn't match."),
    'username_already_used': _("Le nom d'utilisateur \"{0}\" existe déjà. Merci d'en choisir un autre."),
}


class PasswordSetMixin(serializers.Serializer):
    password1 = serializers.CharField(allow_blank=False, trim_whitespace=False)
    password2 = serializers.CharField(allow_blank=False, trim_whitespace=False)

    def validate(self, data):
        password1 = data.get('password1')
        password2 = data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError(auth_error_messages['password_mismatch'])

        password_validation.validate_password(password1, self._context['user'])
        return data

class TermsAcceptanceMixin(serializers.Serializer):
    terms_acceptance = serializers.BooleanField()

    def validate_terms_acceptance(self, terms_acceptance):
        if not terms_acceptance:
            raise ValidationError(auth_error_messages['accept_terms'])
        return terms_acceptance


class LoginSerializer(serializers.Serializer):
    next = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(allow_blank=False, trim_whitespace=False)
    remember_me = serializers.BooleanField()
    username = serializers.CharField(allow_blank=False)

    def validate_username(self, username):
        # Lowercase email (email are stored in lowercase, too much fail auth with capital letters in emails))
        return username.lower()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        request = self._context['request']

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is None:
                raise ValidationError(auth_error_messages['invalid_login'])
            else:
                self.confirm_login_allowed(user)

            self.user = user

        return data

    def confirm_login_allowed(self, user):
        """
        Check if the user is associated to at least one desk.
        Then find its currently connected desk, and check desk.is_active and organization.is_active
        """
        if user.is_superuser:
            return

        desk = get_current_desk(user, self._context['request'].session)

        if not desk or not desk.is_active or not desk.organization.is_active:
            raise ValidationError(auth_error_messages['inactive'])


class RegistrationSerializer(PasswordSetMixin, TermsAcceptanceMixin, serializers.Serializer):
    # Lowercase email (email are stored in lowercase, too much fail auth with capital letters in emails)
    email = EmailLowerCaseField(allow_blank=False)
    organization = serializers.CharField(allow_blank=False)

    def validate_email(self, email):
        if email and PilotUser.objects.filter(email__iexact=email).exists():
            raise ValidationError(auth_error_messages['email_already_used'].format(email))
        return email


class PasswordSetSerializer(PasswordSetMixin, serializers.Serializer):
    pass


class InvitationConfirmSerializer(PasswordSetMixin, TermsAcceptanceMixin, serializers.Serializer):
    pass
