from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _

from pilot.pilot_users.models import PilotUser


class PilotUserCreationForm(forms.ModelForm):
    """A form that creates a user, with no privileges, from the given username and password."""

    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }

    username = forms.RegexField(label=_("Username"), max_length=30,
                                regex=r'^[\w.@+-]+$',
                                help_text=_("160 characters or fewer. Letters, numbers and _ character."),
                                error_messages={
                                    'invalid': _("This value may contain only letters, numbers and _ character.")}
                                )
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification.")
    )

    class Meta:
        model = PilotUser
        fields = ('username',)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            PilotUser._default_manager.get(username=username)
        except PilotUser.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(PilotUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.avatar_changed = True
        if commit:
            user.save()
        return user


class PilotUserChangeForm(forms.ModelForm):
    username = forms.RegexField(
        label=_("Username"),
        max_length=30,
        regex=r"^[\w.@+-]+$",
        help_text=_("160 characters or fewer. Letters, numbers and _ character."),
        error_messages={'invalid': _("This value may contain only letters, numbers and _ character.")}
    )
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>.")
    )

    class Meta:
        model = PilotUser
        fields = ('username',)

    def __init__(self, *args, **kwargs):
        super(PilotUserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the field does not have access to the initial value.
        return self.initial['password']

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and 'avatar' in self.changed_data:
            self.instance.avatar_changed = True
        return avatar
