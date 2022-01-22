from django import forms
from django.utils.translation import ugettext as _


class PasswordRequiredForm(forms.Form):
    """Asks for a password before displaying a public page."""

    password = forms.CharField(label=_("Mot de passe"), widget=forms.PasswordInput)

    def __init__(self, request, password, *args, **kwargs):
        self.request = request
        self.password = password
        super(PasswordRequiredForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        """Validate the correctness of the entered password."""

        password = self.cleaned_data.get('password', '').strip()
        correct_password = self.password

        # Validates that cookies are enabled:
        # request.session.set_test_cookie() must have been called before the validation of this form.
        if not self.request.session.test_cookie_worked():
            raise forms.ValidationError(
                _("Votre navigateur ne semble pas accepter les cookies. Les cookies sont obligatoires."))

        if password != correct_password:
            raise forms.ValidationError(
                _("Mot de passe incorrect. Merci de noter que les mots de passe sont sensibles à la casse."))

        return password
