from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _

# import facebook

from pilot.utils.prosemirror.prosemirror import get_body_input_as_text


class FacebookMaxLengthValidator(object):
    message = _('Contenu trop long. Facebook autorise seulement %(limit_value)s signes '
                '( %(show_value)d signes saisis)')
    code = 'facebook_max_length'
    limit_value = settings.FACEBOOK_MAX_LENGTH

    def __call__(self, value):
        text = get_body_input_as_text(value)
        if len(text) > self.limit_value:
            params = {'limit_value': self.limit_value, 'show_value': len(text), 'value': value}
            raise ValidationError(self.message, code=self.code, params=params)


def post_on_facebook(facebook_item, check_publication_dt=True, user=None):
    """ Try to update a status on facebook. """
    from pilot.social.models import FacebookLog

    log_status = FacebookLog.ERROR_STATUS
    status_id = 'none'
    text = _("Erreur indéfinie")
    status = False

    try:
        fb_credential = facebook_item.channel.facebookcredential
    except AttributeError:
        return False, [{'message': _("La chaîne associée ne dispose pas des droits de publication nécessaires.")}]

    if check_publication_dt:
        if facebook_item.publication_dt > timezone.now():
            return False, [{'message': _("La date de publication est dans le futur")}]

    graph = facebook.GraphAPI(fb_credential.get_relevant_token())

    if fb_credential.is_valid() and fb_credential.can_publish():
        try:
            status = graph.put_object(fb_credential.get_relevant_id(), 'feed',
                                      message=facebook_item.body.encode())
        except facebook.GraphAPIError as error:
            status_id = 'none'
            text = error
        if status:
            facebook_item.publish(user=user)
            status_id = status.get('id')
            text = facebook_item.body
            log_status = FacebookLog.PUBLISHED_STATUS
    facebook_item.facebooklog_set.all().delete()
    FacebookLog.objects.create(
        item=facebook_item,
        status_id=status_id,
        text=smart_str(text),
        status=log_status
    )
    return status, text
