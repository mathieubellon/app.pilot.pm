import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from postmark import PMMail

from pilot.sharings.models import SharingType
from pilot.utils.url import get_fully_qualified_url

logger = logging.getLogger(__name__)

# ===================
# Low-level helpers
# ===================


def make_comment_recipient(user, comment_id):
    return f"reply+c-{user.id}-{comment_id}@{settings.EMAIL_INBOUND_SERVER}"


def make_annotation_recipient(user, item_id, annotation_id):
    return f"reply+a-{user.id}-{item_id}-{annotation_id}@{settings.EMAIL_INBOUND_SERVER}"


def parse_mailbox_hash(mailbox_hash):
    if not mailbox_hash or '-' not in mailbox_hash:
        return None

    splitted = mailbox_hash.split('-')

    # We''re dealing with a comment
    if splitted[0] == 'c':
        return {
            'type': 'comment',
            'user_id': splitted[1],
            'comment_id': splitted[2],
        }
    # We''re dealing with an annotation
    elif splitted[0] == 'a':
        return {
            'type': 'annotation',
            'user_id': splitted[1],
            'item_id': splitted[2],
            'annotation_id': splitted[3],
        }

    return None


def send_smtp(recipient, subject, text_message, html_message=None, reply_to=None):
    try:
        email = EmailMultiAlternatives(
            to=[recipient],
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            reply_to=[reply_to]
        )
        if html_message:
            email.attach_alternative(html_message, 'text/html')

        email.send()
    except Exception as e:
        logger.error(
            'Error while sending email to email address {}'.format(recipient),
            exc_info=True
        )
        # Let the exception bubble up so the user get a 500 error instead of a success message
        raise


def send_postmark(recipient, subject, text_message, html_message=None, reply_to=None, metadata=None):
    try:
        # Force translation to occur,
        # otherwise postmark would try to json-serialize a LazyTranslationString which would fail
        subject = force_text(subject)

        email = PMMail(
            to=recipient,
            subject=subject,
            text_body=text_message,
            html_body=html_message,
            sender=settings.DEFAULT_FROM_EMAIL,
            reply_to=reply_to,
            metadata=metadata
        )
        email.send()
    except Exception as e:
        logger.error(
            'Error while sending email to email address {}'.format(recipient),
            exc_info=True
        )
        # Let the exception bubble up so the user get a 500 error instead of a success message
        raise


def send(recipient, subject, text_message, html_message=None, reply_to=None, metadata=None):
    """
    Low-level helper, that can send any kind of email :
    - Recipient is any email address, from a registred user or an external user.
    - text_message and _html_message are already rendered strings
    - html message is optional ( but highly recommanded )
    """
    # Send the message to the console in dev environment
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        send_smtp(recipient, subject, text_message, html_message, reply_to)
    # In other env, route the mail through postmark
    else:
        send_postmark(recipient, subject, text_message, html_message, reply_to, metadata)


def send_template(recipient, subject, context, text_template, html_template=None, reply_to=None, metadata=None):
    send(
        recipient=recipient,
        subject=subject.format(**context),
        text_message=render_to_string(text_template, context),
        html_message=render_to_string(html_template, context) if html_template else None,
        reply_to=reply_to,
        metadata=metadata,
    )


def send_default_template(recipient, subject,
                          content_title_template=None,
                          content_body_template=None,
                          button_action_text=None,
                          button_action_url=None,
                          context=None,
                          reply_to=None,
                          metadata=None):
    context = context or {}
    if content_title_template:
        context['content_title'] = render_to_string(content_title_template, context)
    if content_body_template:
        context['content_body'] = render_to_string(content_body_template, context)
    if button_action_text:
        context['button_action_text'] = button_action_text.format(**context)
    if button_action_url:
        context['button_action_url'] = button_action_url
    send_template(
        recipient=recipient,
        subject=subject,
        context=context,
        text_template='notifications/email_templates/default.txt',
        html_template='notifications/email_templates/default.html',
        reply_to=reply_to,
        metadata=metadata
    )

# ===================
# Anonymous Emailing (without in-app notification)
# ===================


def send_email_confirmation(user):
    """Sends an email to a user asking for email confirmation."""
    send_default_template(
        recipient=user.email,
        subject=_("Merci de confirmer votre email"),
        button_action_text=_("Cliquez ici pour vérifier votre email"),
        button_action_url=get_fully_qualified_url(user.get_token_url('ui_registration_confirm')),
        context={
            'content_title': _("Bienvenue sur Pilot ! Une dernière étape avant de rejoindre votre compte"),
        }
    )


def send_password_reset(user):
    """Sends an email to this user with instructions and a link for resetting his password."""
    send_default_template(
        recipient=user.email,
        subject=_("Récupération de mot de passe"),
        content_body_template='notifications/content_body/password_reset.txt',
        button_action_text=_("Créer un nouveau mot de passe"),
        button_action_url=get_fully_qualified_url(user.get_token_url('auth_password_reset_confirm')),
        context={
            'content_title': _("Nouveau mot de passe"),
            'user': user
        },
        metadata=dict(
            recipient_id=user.id,
        )
    )


def send_invitation_token(invitation_token):
    """Sends an InvitationToken by email."""
    send_default_template(
        recipient=invitation_token.email,
        subject=_("Invitation - {sender_full_name} vous propose de le rejoindre"),
        content_body_template='notifications/content_body/user_invitation.txt',
        button_action_text=_("Rejoindre {sender_full_name} sur Pilot"),
        button_action_url=get_fully_qualified_url(reverse('ui_invitation_confirm', kwargs={
            'token': invitation_token.token,
        })),
        context={
            'sender_full_name': invitation_token.created_by.get_friendly_name()
        },
        metadata=dict(
            sender_id=invitation_token.created_by.id
        )
    )


def send_reactivated_user(user, desk, reactivated_by):
    """Sends an email to this user when an admin reactivated its account on a desk"""
    send_default_template(
        recipient=user.email,
        subject=_("Réactivation de compte"),
        content_body_template='notifications/content_body/reactivated_user.txt',
        button_action_text=_("Accéder à la page de connexion"),
        button_action_url=get_fully_qualified_url(reverse('auth_login')),
        context={
            'content_title': _("Compte réactivé"),
            'desk': desk,
            'user': user,
            'reactivated_by': reactivated_by.username
        },
        metadata=dict(
            sender_id=reactivated_by.id,
            recipient_id=user.id
        )
    )


def send_sharing(sharing):
    """Sends a sharing by email."""
    sender = sharing.created_by

    if sharing.type == SharingType.ITEM:
        button_action_text = _("Accèder au contenu")
    else:
        button_action_text = _("Accèder aux contenus")

    send_default_template(
        recipient=sharing.email,
        subject=_('Partage de contenu par {sender_full_name}'),
        content_title_template='notifications/content_title/sharing.txt',
        content_body_template='notifications/content_body/sharing.txt',
        button_action_text=button_action_text,
        button_action_url=get_fully_qualified_url(sharing.get_public_absolute_url()),
        context={
            'sharing': sharing,
            'quote': sharing.message,
            'sender_full_name': sender.get_friendly_name(),
        },
        metadata=dict(
            sender_id=sender.id,
        )
    )
