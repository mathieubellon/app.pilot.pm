from django.conf import settings
from django.views.decorators.debug import sensitive_post_parameters
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from pilot.main import forms as common_forms
from pilot.sharings.api.serializers import SharingSerializer
from pilot.sharings.models import Sharing
from pilot.utils.html import render_json


def sharing(request, token, item_pk=None, template_name="sharings/public.html"):
    """
    Public view.
    An anonymous user access a Sharing
    A password may be required.
    """
    sharing = get_object_or_404(Sharing, token=token)

    if request.method == 'GET' and sharing.password:
        checked_sharing_id = request.session.get(settings.SHARING_PASSWORD_CHECKED)
        if checked_sharing_id != sharing.id:
            return HttpResponseRedirect(sharing.get_password_required_url())

    context = {
        'sharing_json': render_json(SharingSerializer(sharing).data)
    }
    return render(request, template_name, context)


@sensitive_post_parameters('password')
def sharing_password_required(request, token, template_name="common/password_required.html"):
    """
    Public view.
    Displayed when a password is required before accessing a Sharing.
    """
    sharing = get_object_or_404(Sharing, token=token)

    # The cookie support will be checked in PasswordRequiredForm.save().
    request.session.set_test_cookie()

    form = common_forms.PasswordRequiredForm(
        data=request.POST or None,
        request=request,
        password=sharing.password
    )

    if request.method == 'POST' and form.is_valid():
        # Mark the id of the checked sharing
        request.session[settings.SHARING_PASSWORD_CHECKED] = sharing.id
        return HttpResponseRedirect(sharing.get_absolute_url())

    context = {
        'form': form,
    }
    return render(request, template_name, context)
