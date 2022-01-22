from django.apps import apps
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db.models import Manager, OuterRef, Q, Subquery, Value
from django.db.models.functions import Concat
from django.db.models.query import QuerySet


class ItemQuerySet(QuerySet):
    def detail_api_prefetch(self):
        return (
            self.select_related(
                'created_by', 'item_type', 'master_translation',
                'project', 'project__category',
                'updated_by', 'workflow_state',
            )
            .prefetch_related(
                'assets', 'channels', 'channels__owners', 'channels__type',
                'owners', 'project__items',
                'sharings', 'sharings__feedbacks', 'sharings__created_by',
                'targets',  'tags', 'tasks', 'tasks__assignees', 'translations',
            )
        )

    def list_api_prefetch(self):
        return (
            self.select_related('created_by', 'project', 'project__category', 'workflow_state')
            .prefetch_related('channels', 'channels__owners', 'owners')
        )

    def filter_by_permissions(self, user):
        if user.is_authenticated and user.permissions.is_restricted_editor:
            return self.filter(
                Q(created_by=user) | Q(project__owners=user) | Q(project__members=user) | Q(channels__owners=user) | Q(owners=user)
            ).distinct()

        return self

    def with_content(self):
        """ Cancel out the  `json_content` deferring made by BaseItemManager """
        if self.query._annotations and '_title' in self.query._annotations:
            del self.query.annotations['_title']
        return self.defer(None)

    def annotate_version(self):
        EditSession = apps.get_model('items.EditSession')

        version_subquery = Subquery(
            EditSession.objects
            .filter(item_id=OuterRef("id"))
            .order_by("-created_at")
            .annotate(version=Concat('major_version', Value('.'), 'minor_version'))
            .values('version')
            [:1]
        )
        return self.annotate(version=version_subquery)


# Passthrough methods from ItemQuerySet to ItemManager
class BaseItemManager(Manager.from_queryset(ItemQuerySet)):
    """
    Base `Item` manager, passing through `ItemQuerySet`.
    By default, will defer the `json_content` field and query `json_content.title` with a KeyTextTransform,
    to improve performances.
    """
    def get_queryset(self):
        return (
            super(BaseItemManager, self).get_queryset()
            .defer('json_content')
            .annotate(_title=KeyTextTransform('title', 'json_content'))
        )


class ItemManager(BaseItemManager):
    """ Return all visible items : trash and active """
    def get_queryset(self):
        return super(ItemManager, self).get_queryset().filter(hidden=False)


class ActiveItemManager(ItemManager):
    """ Returns items active items : visible and not trashed """
    def get_queryset(self):
        return super(ActiveItemManager, self).get_queryset().filter(in_trash=False)


class InTrashItemManager(ItemManager):
    """ Returns items put in trash """
    def get_queryset(self):
        return super(InTrashItemManager, self).get_queryset().filter(in_trash=True)
