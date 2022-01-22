class NotificationType:
    COPY_PROJECT = 'copy_project'
    EXPORT_DESK = 'export_desk'
    EXPORT_XLS = 'export_xls'
    FEED_SAVED_FILTER = 'feed_saved_filter'
    FEED_ACTIVITY = 'feed_activity'
    INTERNAL_SHARED_FILTER = 'internal_shared_filter'
    MENTION_COMMENT = 'mention_comment'
    MENTION_ANNOTATION = 'mention_annotation'
    REMINDER = 'reminder'
    TASK_ASSIGNED = 'task_assigned'
    TASK_UPDATED = 'task_updated'
    TASK_TODO = 'task_todo'
    TASK_DELETED = 'task_deleted'
    VALIDATION_SHARING = 'validation_sharing'
    VALIDATION_IDEA = 'validation_idea'

    CHOICES = [(notif_type, notif_type) for notif_type in (
        COPY_PROJECT, EXPORT_DESK, EXPORT_XLS, FEED_SAVED_FILTER, FEED_ACTIVITY, INTERNAL_SHARED_FILTER,
        MENTION_COMMENT, MENTION_ANNOTATION, REMINDER, TASK_ASSIGNED, TASK_UPDATED, TASK_TODO, TASK_DELETED,
        VALIDATION_SHARING, VALIDATION_IDEA
    )]


class NotificationPreference:
    MENTION = 'mention'
    REMINDER = 'reminder'
    SHARING = 'review'
    TASK = 'task'
