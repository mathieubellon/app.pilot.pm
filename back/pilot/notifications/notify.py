import functools
import logging
from collections import Counter

import arrow

from django.db.models import Q
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from pilot.items.models import EditSession
from pilot.notifications import emailing
from pilot.notifications.jobs import NotifyJob
from pilot.notifications.emailing import make_comment_recipient, make_annotation_recipient
from pilot.notifications.models import Notification, Reminder
from pilot.notifications.const import NotificationType, NotificationPreference
from pilot.notifications.pilot_bot import get_pilot_bot_user
from pilot.sharings.models import SharingStatus
from pilot.utils.diff import format_diff_as_text
from pilot.utils.prosemirror.prosemirror import prosemirror_json_to_text, prosemirror_json_to_html, get_mentions_list
from pilot.utils.url import get_fully_qualified_url


logger = logging.getLogger(__name__)


# ===================
# Low-level helper
# ===================

def notify_sync(desk, type, to_users, message, email_subject,
                send_by=None, linked_object=None, target_url='',
                source_feed=None, data=None,
                content_title_template=None, content_body_template=None, button_action_text=None,
                context={}, format_message=True,
                preference_to_check=None, send_email=True, display_in_app=True,
                reply_to_callback=None):
    """
    Low-level helper, that put together the steps of a notification :
    - Render the text message
    - Create the Notification object
    - Check user preferences, and send an email accordingly, with a link to this notification

    WARNING : this is a synchronous operation, and should not be used directly from the web server.
    Use the "notify" function instead, which will launch an async job in the queue.
    """
    try:
        notifications_sent = []

        # Default text for the action button
        if not button_action_text:
            button_action_text = _('Voir le détail')

        # Render the text message with the context
        if format_message:
            message = message.format(**context)
            button_action_text = button_action_text.format(**context)

        email_context = {
            'content_title': mark_safe(message),
        }
        email_context.update(context)

        if not send_by:
            send_by = get_pilot_bot_user()

        if data is None:
            data = {}

        # Ensure that the user is actually associated to the desk
        for to_user in desk.users.filter(id__in=[u.id for u in to_users]):
            try:
                # When there's a preference to check,
                # the user only get the notifications (email and app) if its preference are set accordingly
                if preference_to_check:
                    user_preferences = to_user.notification_preferences.get(preference_to_check, {})
                    send_email = user_preferences.get('email', True)
                    display_in_app = user_preferences.get('app', True)

                notification = Notification.objects.create(
                    desk=desk,
                    type=type,
                    send_by=send_by,
                    to=to_user,
                    content=message,
                    linked_object=linked_object,
                    target_url=target_url,
                    source_feed=source_feed,
                    data=data,
                    is_read=(not display_in_app)
                )

                notifications_sent.append(notification)

                if send_email:
                    email_context['notifications_settings_url'] = get_fully_qualified_url(
                        reverse('notifications_settings', kwargs={'token': notification.token})
                    )

                    reply_to = None
                    if reply_to_callback:
                        reply_to = reply_to_callback(to_user)

                    emailing.send_default_template(
                        recipient=to_user.email,
                        subject=email_subject,
                        content_title_template=content_title_template,
                        content_body_template=content_body_template,
                        button_action_text=button_action_text,
                        button_action_url=get_fully_qualified_url(notification.get_absolute_url()),
                        context=email_context,
                        reply_to=reply_to,
                        metadata=dict(
                            sender_id=send_by.id,
                            recipient_id=to_user.id,
                            notification_id=notification.id
                        )
                    )
            except:
                logger.error(
                    'Error while notifying user {}'.format(to_user),
                    exc_info=True
                )
    except:
        logger.error('Error during a notify', exc_info=True)

    return notifications_sent


def notify(*args, **kwargs):
    """
    Start an async job for the notify low-level helper
    """
    NotifyJob.launch(*args, **kwargs)

# ===================
# Mention notifications (comment/annotations)
# ===================

YOU_CAN_REPLY_BY_EMAIL = _("Vous pouvez laisser un commentaire en répondant directement à cet e-mail")

GROUP_ALL = 'all'
GROUP_OWNERS = 'owners'
GROUP_MEMBERS = 'members'
GROUP_CHANNEL_OWNERS = 'channelOwners'


def get_mentionned_users(content, instance, desk=None):
    """
    Scan prosemirror doc and extract users @mentionned in a comment or annotation.

    Users can be mentionned directly with @username,
    or indirectly through either @team or @group
    """
    # instance will be either an item or a project, and both of them have a 'desk' attribute
    if not desk:
        desk = instance.desk
    raw_mentions = get_mentions_list(content)

    # 1/ Ventilate mentions by entity
    mentions = {
        'user': [],
        'team': [],
        'group': []
    }
    for mention in raw_mentions:
        mentions[mention['entity']].append(mention['id'])

    # 2/ Shortcut for GROUP_ALL
    if GROUP_ALL in mentions['group']:
        # Shortcut : we must send to all users
        return desk.users.all()

    # 3/ Get users mentioned by their username, or their team
    users = desk.users.filter(Q(id__in=mentions['user']) | Q(teams__id__in=mentions['team']))

    # 4/ Add users from groups
    if isinstance(instance, EditSession):
        instance = instance.item
    if GROUP_OWNERS in mentions['group'] and hasattr(instance, 'owners'):
        users = users | instance.owners.all()
    if GROUP_MEMBERS in mentions['group'] and hasattr(instance, 'members'):
        users = users | instance.members.all()
    if GROUP_CHANNEL_OWNERS in mentions['group']:
        if hasattr(instance, 'channel') and instance.channel:
            users = users | instance.channel.owners.all()
        if hasattr(instance, 'channels'):
            for channel in instance.channels.all():
                users = users | channel.owners.all()

    return users.distinct()


def process_notifications_when_comment_is_created(comment):
    notify_when_mentionned_in_comment(
        comment,
        get_mentionned_users(comment.comment_content, comment.content_object)
    )


def process_notifications_when_comment_is_updated(comment, comment_content_before):
    users_before = set(get_mentionned_users(comment_content_before, comment.content_object))
    users_after = set(get_mentionned_users(comment.comment_content, comment.content_object))

    new_mentions = users_after - users_before
    deleted_mentions = users_before - users_after

    if new_mentions:
        notify_when_mentionned_in_comment(comment, new_mentions)

    if deleted_mentions:
        delete_comment_notification(comment, deleted_mentions)


def notify_when_mentionned_in_comment(comment, to_users):
    """ Scan prosemirror doc, persist notification if any and send mail if user settings allow to"""
    # content_object will be either an item or a project, and both of them have a 'desk' attribute
    instance = comment.content_object
    desk = instance.desk

    comment_text = prosemirror_json_to_text(comment.comment_content)
    comment_html = prosemirror_json_to_html(comment.comment_content)
    reply_to_callback = functools.partial(make_comment_recipient, comment_id=comment.id)

    email_subject = _('@mention sur #{instance.id} {instance}')
    if hasattr(instance, 'project'):
        email_subject += " [{instance.project}]"

    notify(
        desk=desk,
        type=NotificationType.MENTION_COMMENT,
        to_users=to_users,
        message=comment_text,
        format_message=False,
        email_subject=email_subject,
        send_by=comment.user,
        linked_object=instance,
        data={
            'comment': {
                'id': comment.id,
                'comment_content': comment.comment_content
            }
        },
        content_title_template='notifications/content_title/mention_in_comment.txt',
        button_action_text=_("Voir le commentaire sur Pilot"),
        context={
            'instance': instance,
            'content_type': comment.content_type,
            'comment': comment,
            'quote': comment_html,
            'content_body': YOU_CAN_REPLY_BY_EMAIL,
        },
        preference_to_check=NotificationPreference.MENTION,
        reply_to_callback=reply_to_callback
    )


def delete_comment_notification(comment, to_users):
    """ Called when some users are not mentionned anymore on a comment.

    see process_notifications_when_comment_is_updated()
    """
    Notification.objects.filter(
        data__comment_id=comment.id,
        to__in=to_users
    ).delete()


def process_notifications_when_annotation_is_updated(item, annotations_before, annotations_after):
    annotations_after = annotations_after or {}
    annotations_before = annotations_before or {}

    # Build a dict that maps annotations to a count of the mentions in all their comments :
    # { annotation_id : Counter{ @user1: 1 , @user2: 4, ... }, ... }
    def get_mention_map(annotations):
        mention_map = {}
        # Handle the case where annotations == None
        annotations = annotations or {}
        # Guard against fancy annotations type
        if not isinstance(annotations, dict):
            raise ValueError("Annotations should be a dict")

        for annotation_id, annotation in annotations.items():
            mention_map[annotation_id] = Counter()

            for comment in annotation.get('comments', []) + [annotation.get('mainComment', {})]:
                users = get_mentionned_users(comment.get('content'), item)
                mention_map[annotation_id] += Counter(users)

        return mention_map

    for field_name in set(list(annotations_after.keys()) + list(annotations_before.keys())):
        mention_map_before = get_mention_map(annotations_before.get(field_name, {}))
        mention_map_after = get_mention_map(annotations_after.get(field_name, {}))

        # iterate over all the annotation_id present before or after the update
        for annotation_id in set(list(mention_map_before.keys()) + list(mention_map_after.keys())):
            # The mentions before update
            mentions_counter_before = mention_map_before.get(annotation_id, Counter())
            # The mentions after update
            mentions_counter_after = mention_map_after.get(annotation_id, Counter())
            # Note : Counter substraction eliminate negative count, that's the behaviour we need here.
            # Mentions after - Mentions before = new mentions
            new_mentions = (mentions_counter_after - mentions_counter_before).keys()
            # Mentions before - Mentions after = deleted mentions
            deleted_mentions = (mentions_counter_before - mentions_counter_after).keys()
            # Delete notification only if the user is not mentionned at all after the update
            deleted_mentions = [mention for mention in deleted_mentions if mentions_counter_after[mention] == 0]

            if new_mentions:
                notify_when_mentionned_in_annotation(
                    item,
                    annotations_after[field_name][annotation_id],
                    new_mentions
                )

            if deleted_mentions:
                delete_annotation_notification(
                    annotation_id,
                    deleted_mentions
                )


def notify_when_mentionned_in_annotation(item, annotation, to_users):
    """ Called when some users are mentionned for the first time in an annotation.

    see process_notifications_when_annotation_is_updated()
    """
    # For now, always take the last comment.
    # Its either a reply, or the main comment
    # This will handle correctly only creations, and not updates
    comments = annotation.get('comments', [])
    if comments:
        comment = comments[-1]
    else:
        comment = annotation.get('mainComment', {})

    try:
        author_id = comment.get('user', {}).get('id')
        author = item.desk.users.get(id=author_id)
    except ObjectDoesNotExist:
        return

    comment_text = prosemirror_json_to_text(comment.get('content'))
    comment_html = prosemirror_json_to_html(comment.get('content'))
    reply_to_callback = functools.partial(
        make_annotation_recipient,
        item_id=item.id,
        annotation_id=annotation.get('id')
    )

    notify(
        desk=item.desk,
        type=NotificationType.MENTION_ANNOTATION,
        # Cast to a list to ensure we don't try to pickle an iterator
        to_users=list(to_users),
        message=comment_text,
        format_message=False,
        email_subject=_('@mention sur #{item.id} {item} [{item.project}]'),
        send_by=author,
        linked_object=item,
        data=dict(
            annotation_uuid=annotation.get('id', None),
            comment=comment
        ),
        content_title_template='notifications/content_title/mention_in_annotation.txt',
        button_action_text=_("Voir l'annotation sur Pilot"),
        context={
            'item': item,
            'author': author,
            'quote': comment_html,
            'content_body': YOU_CAN_REPLY_BY_EMAIL,
        },
        preference_to_check=NotificationPreference.MENTION,
        reply_to_callback=reply_to_callback
    )


def delete_annotation_notification(annotation_id, to_users):
    """ Called when some users are not mentionned anymore on an annotation.

    see process_notifications_when_annotation_is_updated()
    """
    Notification.objects.filter(
        data__annotation_uuid=annotation_id,
        to__in=to_users
    ).delete()


# ===================
# Task Notifications
# ===================


def notify_task(notification_type, author, task, to_users, email_subject, message, button_action_text, data={}):
    linked_object = task.get_linked_object()
    notify(
        desk=task.desk,
        type=notification_type,
        to_users=to_users,
        message=message,
        email_subject=email_subject,
        send_by=author,
        linked_object=task,
        content_body_template='notifications/content_body/task.txt',
        button_action_text=button_action_text,
        context={
            'author': author,
            'linked_object': linked_object,
            'object_type': str(linked_object._meta.verbose_name).lower(),
            'task': task
        },
        preference_to_check=NotificationPreference.TASK,
        data=data
    )


def notify_when_assigned_to_task(author, task, to_users):
    """
    Notify the users that has been newly assigned to a task
    """
    notify_task(
        notification_type=NotificationType.TASK_ASSIGNED,
        author=author,
        task=task,
        to_users=to_users,
        message=_("{author} vous a assigné une tâche ({task.name}) sur le {object_type} #{linked_object.id} {linked_object}"),
        email_subject=_("Nouvelle tâche sur #{linked_object.id} {linked_object}"),
        button_action_text=_("Voir le détail de la tâche")
    )


def notify_when_my_task_updated(author, task, to_users, diff):
    """
    Notify the users assigned to a task when the task is updated
    """
    notify_task(
        notification_type=NotificationType.TASK_UPDATED,
        author=author,
        task=task,
        to_users=to_users,
        message="{0}\n\n{1}".format(
            _("{author} a modifié une tâche ({task.name}) sur le {object_type} #{linked_object.id} {linked_object}"),
            format_diff_as_text(task, diff)
        ),
        email_subject=_("Tâche modifiée sur #{linked_object.id} {linked_object}"),
        button_action_text=_("Voir le détail de la tâche"),
        data={
            'diff': diff
        }
    )


def notify_when_task_todo(author, task):
    """
    Notify the users when a task he's assigned to is the next task to do
    """
    message = _("{author} vient de terminer une tâche sur le {object_type} #{linked_object.id} {linked_object}. "
                "Nous vous tenons au courant car vous êtes responsable (ou parmi les responsables) "
                "de la tâche suivante ({task.name})")
    notify_task(
        notification_type=NotificationType.TASK_TODO,
        author=author,
        task=task,
        to_users=task.assignees.all(),
        message=message,
        email_subject=_("Tâche réalisée sur #{linked_object.id} {linked_object}"),
        button_action_text=_("Voir le détail de la tâche")
    )


def notify_when_task_deleted(author, task):
    """
    Notify the users when a task he was assigned to has been deleted
    """
    message = _("{author} a supprimé une tâche sur le {object_type} #{linked_object.id} {linked_object}, sur laquelle "
                "vous étiez assigné(e) ({task.name})")
    notify_task(
        notification_type=NotificationType.TASK_DELETED,
        author=author,
        task=task,
        to_users=task.assignees.all(),
        message=message,
        email_subject=_("Tâche supprimée sur #{linked_object.id} {linked_object}"),
        button_action_text=_("Voir le {object_type}")
    )


# ===================
# Reminder notifications
# ===================
REMINDER_DATE_FORMAT = 'ddd. D MMMM'


def notify_ripe_reminder(reminder):
    if reminder.target_type == Reminder.TARGET_TYPE_TASK_DEADLINE:
        task = reminder.target_task
        target_display = f"{task} ({task.get_linked_object()})"
        message = _("Rappel : La tâche {target_display} est à effectuer pour {target_date_time}")
    elif reminder.target_type == Reminder.TARGET_TYPE_ASSET_RIGHT_EXPIRY:
        asset_right = reminder.target_asset_right
        target_display = f"{asset_right.medium.name} ({asset_right.asset})"
        message = _("Rappel : Les droits de {target_display} expirent {target_date_time}")
    else:
        target_display = str(reminder.get_target())
        message = _("Rappel : {target_display} pour {target_date_time}")

    # IMPORTANT, please note.
    # We use purposedly a notify_sync() instead of a classical notify().
    # This notify_ripe_reminder function is called from the notify_reminder command.
    # The command needs the notifications_sent return value.
    # Because we are in a CRON job, and not the web server, there's no adverse performance implications.
    return notify_sync(
        desk=reminder.desk,
        type=NotificationType.REMINDER,
        to_users=[reminder.user],
        message=message,
        email_subject="[Rappel] Le {target_date_time} : {target_display}",
        linked_object=reminder.get_target(),
        data={
            'reminder_id': reminder.id
        },
        context={
            'target_display': target_display,
            'target_date_time': (arrow.get(reminder.get_target_date_time())
                .format(REMINDER_DATE_FORMAT, locale=reminder.user.language))
        },
        preference_to_check=NotificationPreference.REMINDER
    )

# ===================
# Other Notifications
# ===================


def notify_internal_shared_filter(shared_filter):
    """Sends an email to the recipients of a SavedFilter internal sharing."""
    notify(
        desk=shared_filter.saved_filter.desk,
        type=NotificationType.INTERNAL_SHARED_FILTER,
        to_users=shared_filter.users.all(),
        message=prosemirror_json_to_text(shared_filter.message),
        format_message=False,
        email_subject=_('{sender} a partagé le filtre "{saved_filter}"'),
        send_by=shared_filter.created_by,
        linked_object=shared_filter,
        content_title_template='notifications/content_title/internal_shared_filter.txt',
        button_action_text=_("Voir le filtre sur Pilot"),
        context={
            'sender': shared_filter.created_by,
            'saved_filter': shared_filter.saved_filter,
            'quote': prosemirror_json_to_html(shared_filter.message),
            'content_body': _("Pour le retrouver facilement, vous pouvez copier ce filtre dans vos filtres personnels."),
        },
    )


def notify_sharing_feedback(feedback):
    """Sends an email to the Revision creator with the verdict or the reviewer."""
    sharing = feedback.sharing

    # Force gettext to the sender's locale as anonymous users doesn't have locale preferences.
    from django.utils import translation
    translation.activate(sharing.created_by.language)

    if feedback.status == SharingStatus.APPROVED:
        email_subject = _("Approbation de contenu partagé")
        verdict = _("approuvé")

    elif feedback.status == SharingStatus.REJECTED:
        email_subject =_("Rejet de contenu partagé")
        verdict = _("rejeté")

    elif feedback.status == SharingStatus.EDITED:
        email_subject =_("Contenu partagé édité")
        verdict = _("édité")

    notify(
        desk=feedback.desk,
        type=NotificationType.VALIDATION_SHARING,
        to_users=[sharing.created_by],
        message=_("{reviewer_email} a {verdict} le contenu {title}"),
        email_subject=email_subject,
        linked_object=feedback,
        content_body_template='notifications/content_body/review_validation.txt',
        button_action_text=_("Accèder au contenu {title}"),
        context={
            'reviewer_email': sharing.email,
            'comment': feedback.feedback_message,
            'verdict': verdict,
            'title': feedback.item.title
        },
        preference_to_check=NotificationPreference.SHARING
    )

    translation.deactivate()


def notify_idea_validation(instance, is_accepted):
    email_subject = _("Votre proposition de {object_type} a été {verdict}")
    content_body_template = 'notifications/content_body/idea_validation.txt'
    context={
        'object_type': str(instance._meta.verbose_name).lower(),
        'object_name': str(instance),
        'verdict':  _("validée") if is_accepted else _("rejetée"),
    }

    notify(
        desk=instance.desk,
        type=NotificationType.VALIDATION_IDEA,
        to_users=[instance.created_by],
        message=_('Votre proposition de {object_type} "{object_name}" a été {verdict}.'),
        email_subject=email_subject,
        send_by=instance.created_by,
        linked_object=instance,
        content_body_template=content_body_template,
        context=context,
    )



