import logging

from django.db import transaction
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from pilot.items.models import Item
from pilot.items.api.light_serializers import ItemLightSerializer
from pilot.itemsfilters.models import SavedFilter
from pilot.itemsfilters.saved_filter import get_items_ids_in_saved_filter
from pilot.notifications.models import NotificationFeed
from pilot.notifications.const import NotificationType
from pilot.notifications.notify import notify


logger = logging.getLogger(__name__)


SAVED_FILTER_ENTERED = 'entered'
SAVED_FILTER_EXITED = 'exited'
SAVED_FILTER_UPDATED = 'updated'


def notify_activity_feeds(activity):
    """
    Send a Notification on all NotificationFeed concerned by an Activity

    Called after an Activity creation, this will notify all the interested users.
    """
    feeds = NotificationFeed.objects.filter(
        desk=activity.desk,
        feed_type=NotificationFeed.FEED_TYPE_ACTIVITY_STREAM
    ).filter(
        # PositiveIntegerField sucks at handling the __in filter with a Non inside it.
        # It sends the 'None' String to the db instead of the NULL constant, which mess up everything.
        # Here we fall back on manually constructing an OR close
        Q(activity_verb="") | Q(activity_verb=activity.verb),
        Q(activity_content_type=None) | Q(activity_content_type=activity.target_content_type),
        Q(activity_object_id=None) | Q(activity_object_id=activity.target_object_id),
        Q(activity_actor=None) | Q(activity_actor=activity.actor),
    )

    context = activity.get_target_display_context()
    context.update({
        'actor_display': activity.get_actor_display(),
        'verb_display': activity.get_verb_display()
    })
    for feed in feeds:
        notify(
            desk=feed.desk,
            type=NotificationType.FEED_ACTIVITY,
            to_users=[feed.user],
            message=_('Activité sur {target_text} : {verb_display} par {actor_display}'),
            email_subject=_('Activité sur {target_text}'),
            linked_object=activity.target,
            source_feed=feed,
            button_action_text=_("Voir {target_text}"),
            context=context
        )


def notify_saved_filter(feed, instance_id, action):
    """
    Send a Notification on a NotificationFeed,
    because an object entered or exited the SavedFilter.
    """
    if action == SAVED_FILTER_ENTERED:
        message=_('[Entrée dans le filtre] Le contenu "{item}" a été ajouté au filtre "{feed.saved_filter}"')
        email_subject=_('Activité sur "{feed.saved_filter}"')
    elif action == SAVED_FILTER_EXITED:
        message=_('[Sortie du filtre] Le contenu "{item}" a été retiré du filtre "{feed.saved_filter}"')
        email_subject=_('Activité sur "{feed.saved_filter}"')
    elif action == SAVED_FILTER_UPDATED:
        message=_('[Mise à jour] Contenu "{item}" appartenant au filtre "{feed.saved_filter}"')
        email_subject=_('Activité sur "{feed.saved_filter}"')
    else:
        raise ValueError("Incorrect action value : {}".format(action))

    item = Item.accessible_objects.get(id=instance_id)
    notify(
        desk=feed.desk,
        type=NotificationType.FEED_SAVED_FILTER,
        to_users=[feed.user],
        message=message,
        email_subject=email_subject,
        linked_object=feed.saved_filter,
        source_feed=feed,
        data=dict(
            saved_filter_action=action,
            item=ItemLightSerializer(item).data
        ),
        button_action_text=_("Voir {feed.saved_filter}"),
        context={
            'feed': feed,
            'item': item
        },
        send_email=feed.send_email,
        display_in_app=feed.display_in_app,
    )


def update_saved_filters_and_notify(desk, updated_instances):
    # Update only SavedFilters which are associated to a NotificationFeed
    feeds = NotificationFeed.objects.filter(
        desk=desk,
        feed_type=NotificationFeed.FEED_TYPE_ITEM_SAVED_FILTER,
    )
    for feed in feeds:
        try:
            # We need a transaction + a select_for_update()
            # to ensure that concurrent jobs won't tinker concurrently with saved_filter.notification_feed_instance_ids
            with transaction.atomic():
                saved_filter = SavedFilter.objects.select_for_update().get(id=feed.saved_filter_id)
                old_ids = set(saved_filter.notification_feed_instance_ids)
                new_ids_list = get_items_ids_in_saved_filter(saved_filter)
                new_ids = set(new_ids_list)

                # Update the id list if it has been updated
                if old_ids != new_ids:
                    saved_filter.notification_feed_instance_ids = new_ids_list
                    saved_filter.save()

            for updated_instance in updated_instances:
                # We notify for updated model if :
                # 1/ The updated model is actually an Item (not a Task)
                # 2/ The updated id were into the filter before AND after the update
                if isinstance(updated_instance, Item) and updated_instance.id in (old_ids & new_ids):
                    # Notify item update
                    notify_saved_filter(feed, updated_instance.id, SAVED_FILTER_UPDATED)

                for instance_id in (new_ids - old_ids):
                    # Notify item enter
                    notify_saved_filter(feed, instance_id, SAVED_FILTER_ENTERED)

                for instance_id in (old_ids - new_ids):
                    # Notify item exit
                    notify_saved_filter(feed, instance_id, SAVED_FILTER_EXITED)
        except:
            logger.error(f"Failed to update and notify SavedFilter {feed.saved_filter_id} on NotificationFeed {feed.id}", exc_info=True)
