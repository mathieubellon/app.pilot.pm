from django.contrib.contenttypes.models import ContentType

from pilot.activity_stream.jobs import create_activity
from pilot.activity_stream.models import Activity
from pilot.comments.models import Comment
from pilot.items.models import Item
from pilot.notifications import notify


def create_comment_and_activity(instance, comment_content, user):
    """
    We may create a comment from a postmark inbound message,
    so we cannot consider there will be a request object with an authenticated user.
    """
    # Instance will be either an item or a project, and both of them have a 'desk' attribute
    desk = instance.desk
    comment_content = comment_content or {}
    data = {}

    if isinstance(instance, Item):
        data['version'] = instance.last_session.get_version_display()

    comment = Comment.objects.create(
        desk=desk,
        user=user,
        user_email=user.email,
        comment_content=comment_content,
        content_object=instance,
        data=data
    )

    activity = create_activity(
        actor=user,
        desk=desk,
        verb=Activity.VERB_COMMENTED,
        target=instance,
        action_object=comment
    )

    notify.process_notifications_when_comment_is_created(comment)

    return activity


def get_comments_queryset(instance):
    """
    Returns all the comments associated to a model instance in the system
    """
    return (
        Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(instance.__class__),
            object_id=instance.id
        )
        .select_related('user')
        .prefetch_related('content_object')
        .order_by('-submit_date')
    )
