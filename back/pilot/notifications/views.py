import json
import logging

# Silence joblib warning until this pull request is accepted:
# https://github.com/mailgun/talon/pull/207
import warnings
def warn(*args, **kwargs):
    pass
old_warn = warnings.warn
warnings.warn = warn

from talon import quotations
from talon.signature.bruteforce import extract_signature

# This is only needed when using machine learning. For now we'll just use bruteforce.
# import talon
# talon.init()

warnings.warn = old_warn

from django.db import ProgrammingError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, Http404, HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone, translation
from django.views.decorators.csrf import csrf_exempt

from pilot.activity_stream.comment import create_comment_and_activity
from pilot.activity_stream.models import Activity
from pilot.assets.models import Asset
from pilot.channels.models import Channel
from pilot.comments.models import Comment
from pilot.desks.utils import connect_to_desk
from pilot.item_types.models import ItemType
from pilot.items.models import Item
from pilot.labels.models import Label
from pilot.notifications import emailing
from pilot.notifications.models import Notification
from pilot.notifications.notify import get_mentionned_users, notify_when_mentionned_in_annotation
from pilot.notifications.pilot_bot import get_pilot_bot_user
from pilot.pilot_users.models import PilotUser
from pilot.projects.models import Project
from pilot.targets.models import Target
from pilot.utils.html import render_json
from pilot.utils.prosemirror.prosemirror import convert_text_to_prosemirror_doc

logger = logging.getLogger(__name__)

# Alias for concise syntax
A = Activity

COMMON_VERBS = (
    A.VERB_CREATED,
    A.VERB_UPDATED,
    A.VERB_DELETED
)

ACTIVITY_FEED_SPEC = {
    'verb_choices': dict(A.ACTIVE_VERB_CHOICES),
    'common_verbs': COMMON_VERBS,
    'models': (
        {
            'model': Item,
            'search_api': reverse_lazy('dashboard'),
            'verbs': (
                A.VERB_ASSET_LINKED,
                A.VERB_ASSET_UNLINKED,
                A.VERB_COMMENTED,
                A.VERB_PUT_IN_TRASH,
                A.VERB_RESTORED,
                A.VERB_RESTORED_FROM_TRASH,
                A.VERB_SHARED,
                A.VERB_STARTED_EDIT_SESSION,
                A.VERB_TASK_CREATED,
                A.VERB_TASK_DELETED,
                A.VERB_TASK_DONE,
                A.VERB_TASK_UPDATED,
                A.VERB_UPDATED_WORKFLOW,
                A.VERB_CREATE_MAJOR_VERSION,
            )
        },
        {
            'model': Project,
            'search_api': 'TODO',
            'verbs': (
                A.VERB_ASSET_LINKED,
                A.VERB_ASSET_UNLINKED,
                A.VERB_CLOSED,
                A.VERB_COMMENTED,
                A.VERB_REOPENED,
            )
        },
        {'model': Asset},
        {'model': Channel},
        {'model': Target},
        {'model': Label},
        {'model': ItemType},
        {
            'model': PilotUser,
            'verbs': (
                A.VERB_JOINED_TEAM,
            )
        },
    )
}

# Transform the Model class into their corresponding label & content type id
for model_spec in ACTIVITY_FEED_SPEC['models']:
    model = model_spec.pop('model')
    try:
        content_type = ContentType.objects.get_for_model(model)
        model_spec['content_type_id'] = content_type.id
        model_spec['label'] = model._meta.verbose_name.capitalize()
    except ProgrammingError: # Will happen on empty database
        pass


@login_required
def go_to_notification_target(request, token=None, notification_id=None):
    if token:
        notification = get_object_or_404(Notification, token=token)
    elif notification_id:
        notification = get_object_or_404(Notification, id=notification_id)
    else:
        raise Http404('Need a token')

    error_message = None

    if notification.to != request.user:
        error_message = _("L'utilisateur {} n'est pas le destinataire de cette notification").format(
            request.user.username
        )

    try:
        connect_to_desk(notification.desk, request)
    except PermissionDenied as e:
        error_message = str(e)

    target_url = notification.get_target_url()

    if target_url is None:
        error_message = _("La cible de cette notification n'existe plus")

    if error_message:
        return render(request, 'message.html', {'message': error_message})

    else:
        return redirect(target_url)


def notifications_settings(request, token=None, template_name='notifications/settings.html'):
    # Ensure there's a corresponding notification
    notification = get_object_or_404(Notification, token=token)
    user = notification.to
    translation.activate(user.language)
    context = {
        'token': token,
        'notification_user': user,
        'notification_preferences': render_json(user.notification_preferences)
    }
    return render(request, template_name, context)


@csrf_exempt
def postmark_inbound_webhook(request):
    logger.info(f"Start handling postmark inbound email")

    try:
        postmark_data = json.loads(request.body)

        parse_result = emailing.parse_mailbox_hash(postmark_data.get('MailboxHash'))
        if not parse_result:
            return HttpResponse()

        # Let's try to extract the reply (without signature) from the full body
        text_body = postmark_data.get('TextBody')
        full_reply = quotations.extract_from_plain(text_body)
        reply_text, reply_signature = extract_signature(full_reply)
        reply_as_prosemirror_doc = convert_text_to_prosemirror_doc(reply_text)

        user = PilotUser.objects.get(id=parse_result['user_id'])

        if parse_result['type'] == 'comment':
            original_comment = Comment.objects.get(id=parse_result['comment_id'])
            instance = original_comment.content_object
            create_comment_and_activity(
                instance=instance,
                comment_content=reply_as_prosemirror_doc,
                user=user
            )

        if parse_result['type'] == 'annotation':
            item = Item.objects.get(id=parse_result['item_id'])
            annotation_id = parse_result['annotation_id']

            # Search for the corresponding annotation
            for field_name, annotations in item.annotations.items():
                if annotation_id not in annotations:
                    continue
                annotation = annotations[annotation_id]
                new_comment = dict(
                    date=timezone.now().isoformat(),
                    content=reply_as_prosemirror_doc,
                    user=dict(
                        id=user.id,
                        avatar=user.get_avatar_url(),
                        username=user.username
                    )
                )
                annotation['comments'].append(new_comment)
                item.save()

                mentions = get_mentionned_users(reply_as_prosemirror_doc, item)
                notify_when_mentionned_in_annotation(item, annotation, mentions)
                break

        return HttpResponse()
    except:
        logger.error('Postmark inbound message handling error', exc_info=True)
        return HttpResponseServerError()

    finally:
        logger.info(f"End handling postmark inbound email")


AUTO_RESPONDER = 'AutoResponder'
HARD_BOUNCE = 'HardBounce'
SOFT_BOUNCE = 'SoftBounce'

@csrf_exempt
def postmark_bounce_webhook(request):
    logger.info(f"Start handling postmark bounced email")

    try:
        postmark_data = json.loads(request.body)
        type = postmark_data.get('Type')

        # For now, we handle only Auto Responder bounces
        if type not in [AUTO_RESPONDER, HARD_BOUNCE, SOFT_BOUNCE]:
            return HttpResponse()

        sender_user, recipient_user = None, None

        metadata = postmark_data.get('Metadata', {})
        sender_id = metadata.get('sender_id')

        # No need to bother the bot, he does not really care...
        if not sender_id or str(sender_id) == str(get_pilot_bot_user().id):
            return HttpResponse()

        sender_user = PilotUser.objects.get(id=sender_id)
        recipient_id = metadata.get('recipient_id')
        if recipient_id:
            recipient_user = PilotUser.objects.get(id=recipient_id)

        # Force gettext to the recipient's locale, because this view is called by postmark without the locale.
        translation.activate(sender_user.language)

        if recipient_user:
            recipient = recipient_user.get_short_name()
            intro = _("Vous avez notifié {recipient} sur Pilot").format(recipient=recipient)
        else:
            recipient = postmark_data.get('Email')
            intro = _("Vous avez contacté {recipient} depuis Pilot").format(recipient=recipient)

        if type == AUTO_RESPONDER:
            reason = _("mais cette personne est actuellement absente")
        elif type == HARD_BOUNCE:
            reason = _("mais l'adresse email revient en erreur, il y a peut-être une erreur de frappe")
        elif type == SOFT_BOUNCE:
            reason = _("mais l'adresse email est temporairement injoignable, il faudra ré-essayer plus tard")

        emailing.send_template(
            recipient=sender_user.email,
            subject=_("Impossible de délivrer un email à {recipient}"),
            text_template='notifications/email_templates/bounce_notification.txt',
            context=dict(
                recipient=recipient,
                intro=intro,
                reason=reason,
                subject=postmark_data.get('Subject', ''),
                bounce_details=postmark_data.get('Details', ''))
        )

        return HttpResponse()
    except:
        logger.error('Postmark bounce message handling error', exc_info=True)
        return HttpResponseServerError()

    finally:
        logger.info(f"Start handling postmark bounced email")
