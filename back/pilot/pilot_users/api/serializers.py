from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import password_validation
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.validators import UniqueValidator

from pilot.messaging.api.serializers import MessageSerializer
from pilot.pilot_users.api.auth_serializers import auth_error_messages
from pilot.pilot_users.models import InvitationToken, PilotUser, Team
from pilot.utils.api.serializers import EmailLowerCaseField, SmartPrimaryKeyRelatedField


class UserPermissionsSerializer(serializers.Serializer):
    permission = serializers.ReadOnlyField()
    is_admin = serializers.ReadOnlyField()
    is_organization_admin = serializers.ReadOnlyField()
    is_editor = serializers.ReadOnlyField()
    is_restricted_editor = serializers.ReadOnlyField()


class TeamSerializer(serializers.ModelSerializer):
    # users = PilotUserLightSerializer(many=True)
    # users_id = SmartPrimaryKeyRelatedField(source='users', many=True, required=False, allow_null=True)

    class Meta:
        model = Team
        fields = (
            'description',
            'id',
            'name',
            # 'users',
            # 'users_id'
        )

    def validate_name(self, name):
        """
        Validates that the name is not already used
        """
        if name:
            desk = self._context['request'].desk
            already_in_use = Team.objects.filter(name__iexact=name, desk=desk)
            if self.instance:
                already_in_use = already_in_use.exclude(pk=self.instance.pk)
            if already_in_use.exists():
                raise serializers.ValidationError(
                    _("Le nom d'équipe \"{0}\" existe déjà. Merci d'en choisir un autre.").format(name))

            username_already_in_use = PilotUser.objects.filter(username__iexact=name)
            if username_already_in_use.exists():
                raise serializers.ValidationError(
                    _("Le nom d'utilisateur \"{0}\" existe déjà. "
                      "Pour éviter toute confusion, vous ne pouvez pas créer une équipe avec le même nom. "
                      "Merci de choisir un autre nom d'équipe, ou supprimer cet utilisateur").format(name))

        return name


class PilotUserUltraLightSerializer(serializers.ModelSerializer):
    """
    Serializer with lighten data, aimed at returning a large number of items into the item calendar/list API
    """
    class Meta:
        model = PilotUser
        fields = (
            'username',
        )


class PilotUserLightSerializer(serializers.ModelSerializer):
    avatar = serializers.ReadOnlyField(source='get_avatar_url')

    class Meta:
        model = PilotUser
        fields = (
            'avatar',
            'email',
            'first_name',
            'id',
            'last_name',
            'username',
            'wiped'
        )


class PilotUserSerializer(serializers.ModelSerializer):
    avatar = serializers.ReadOnlyField(source='get_avatar_url')
    email = EmailLowerCaseField()
    # This value will be added by an annotation on the queryset into the UsersViewSet
    permission = serializers.ReadOnlyField()
    teams = TeamSerializer(many=True, read_only=True)
    teams_id = SmartPrimaryKeyRelatedField(source='teams', many=True, read_only=True)

    class Meta:
        model = PilotUser
        fields = (
            'avatar',
            'email',
            'first_name',
            'permission',
            'id',
            'job',
            'last_name',
            'localization',
            'phone',
            'teams',
            'teams_id',
            'username',
            'wiped',
        )


class PilotUserMeSerializer(PilotUserSerializer):
    config_calendar = serializers.JSONField(source='user_in_desk.config_calendar')
    config_dashboard = serializers.JSONField(source='user_in_desk.config_dashboard')
    desks = serializers.SerializerMethodField()
    permissions = UserPermissionsSerializer(read_only=True)
    unread_messages = serializers.SerializerMethodField()
    unread_notifications_count = serializers.SerializerMethodField()
    undone_tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = PilotUser
        fields = PilotUserSerializer.Meta.fields + (
            'config_calendar',
            'config_dashboard',
            'desks',
            'language',
            'login_menu',
            'notification_preferences',
            'permissions',
            'timezone',
            'unread_messages',
            'unread_notifications_count',
            'undone_tasks_count'
        )
    
    def __init__(self, *args, **kwargs):
        super(PilotUserMeSerializer, self).__init__(*args, **kwargs)
        # DRF ModelSerializer use the uniqueness of the fields to generate a UniqueValidator,
        # which takes precedence over our own validators.
        # But this is not desired, because we want to check the username in an case-insensitive-way.
        self.fields['username'].validators = [
            validator for validator in self.fields['username'].validators
            if not isinstance(validator, UniqueValidator)
        ]
        self.fields['email'].validators = [
            validator for validator in self.fields['email'].validators
            if not isinstance(validator, UniqueValidator)
        ]

    def _get_desk(self):
        return self._context['request'].desk

    def get_desks(self, user):
        return [{
            'id': desk.id,
            'name': desk.name,
            'undone_tasks_count': user.get_undone_tasks_count(desk),
            'unread_notifications_count': user.get_unread_notifications_count(desk),
        } for desk in user.desks.filter(is_active=True).order_by('name')]

    def get_unread_messages(self, user):
        return MessageSerializer(user.messages.filter(user_message_set__read_at=None).distinct(), many=True).data

    def get_undone_tasks_count(self, user):
        return user.get_undone_tasks_count(self._get_desk())

    def get_unread_notifications_count(self, user):
        return user.get_unread_notifications_count(self._get_desk())

    def validate_email(self, email):
        """
        Validates that the username is not already used
        """
        if email:
            already_in_use = PilotUser.objects.filter(email__iexact=email)
            if self.instance:
                already_in_use = already_in_use.exclude(pk=self.instance.pk)
            if already_in_use.exists():
                raise serializers.ValidationError(auth_error_messages['email_already_used'].format(email))

        return email

    def validate_username(self, username):
        """
        Validates that the username is not already used
        """
        if username:
            already_in_use = PilotUser.objects.filter(username__iexact=username)
            if self.instance:
                already_in_use = already_in_use.exclude(pk=self.instance.pk)
            if already_in_use.exists():
                raise serializers.ValidationError(auth_error_messages['username_already_used'].format(username))

        return username

    def update(self, user, validated_data):
        validated_user_in_desk = validated_data.pop('user_in_desk', {})
        config_calendar = validated_user_in_desk.get('config_calendar')
        config_dashboard = validated_user_in_desk.get('config_dashboard')

        for attr, value in validated_data.items():
            setattr(user, attr, value)
        user.save()

        user_in_desk = user.user_in_desk
        if config_calendar is not None:
            user_in_desk.config_calendar = config_calendar
        if config_dashboard is not None:
            user_in_desk.config_dashboard = config_dashboard
        user_in_desk.save()

        return user


class ChangeNotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PilotUser
        fields = (
            'notification_preferences',
        )


class ChangePasswordSerializer(serializers.ModelSerializer):
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)
    old_password = serializers.CharField(write_only=True)

    class Meta:
        model = PilotUser
        fields = (
            'new_password1',
            'new_password2',
            'old_password',
        )

    def validate_old_password(self, old_password):
        """
        Validates that the old_password field is correct.
        """
        if not self.instance.check_password(old_password):
            raise serializers.ValidationError(auth_error_messages['password_incorrect'])
        return old_password

    def validate(self, data):
        password1 = data.get('new_password1')
        password2 = data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise serializers.ValidationError(auth_error_messages['password_mismatch'])
        password_validation.validate_password(password2, self.instance)
        return data

    def update(self, user, validated_data):
        user.set_password(validated_data["new_password1"])
        user.save()
        return user


class PilotInvitationSerializer(serializers.ModelSerializer):
    teams = TeamSerializer(many=True, read_only=True)
    teams_id = SmartPrimaryKeyRelatedField(source='teams', many=True, required=False, allow_null=True)

    class Meta:
        model = InvitationToken
        fields = (
            'created_at',
            'id',
            'email',
            'permission',
            'teams',
            'teams_id'
        )

    def create(self, validated_data):
        # Use the 'empty' marker because None may be a valid value to set an empty m2m
        teams = validated_data.pop('teams', empty)

        invitation = super(PilotInvitationSerializer, self).create(validated_data)

        if teams is not empty:
            invitation.teams.set(teams or [])

        return invitation
