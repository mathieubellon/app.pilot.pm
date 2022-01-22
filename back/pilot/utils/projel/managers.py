from django.db.models import Count, Manager, Q
from django.db.models.query import QuerySet

from pilot.utils import states

PROJECT_MODEL_NAME = 'project'
CHANNEL_MODEL_NAME = 'channel'


class ProjelQuerySet(QuerySet):
    def detail_api_prefetch(self):
        if self.model._meta.model_name == PROJECT_MODEL_NAME:
            return (
                self.select_related('created_by', 'category', 'priority', 'updated_by')
                .prefetch_related(
                    'assets', 'channels', 'channels__owners', 'members', 'owners',
                    'sharings', 'sharings__feedbacks', 'sharings__created_by',
                    'targets', 'tasks', 'tags'
                )
                .annotate(items_count=Count('items', filter=Q(items__in_trash=False, items__hidden=False)))
            )

        elif self.model._meta.model_name == CHANNEL_MODEL_NAME:
            return (
                self.select_related('created_by', 'type', 'updated_by')
                .prefetch_related(
                    'assets', 'owners',
                    'sharings', 'sharings__feedbacks', 'sharings__created_by',
                    'tasks'
                )
                .annotate(items_count=Count('items', filter=Q(items__in_trash=False, items__hidden=False)))
            )

    def list_api_prefetch(self):
        if self.model._meta.model_name == PROJECT_MODEL_NAME:
            return self.select_related('created_by', 'category', 'priority')
        elif self.model._meta.model_name == CHANNEL_MODEL_NAME:
            return self.select_related('created_by', 'type')

    def filter_by_permissions(self, user):
        if user.is_authenticated and user.permissions.is_restricted_editor:
            if self.model._meta.model_name == PROJECT_MODEL_NAME:
                return self.filter(
                    Q(created_by=user) | Q(owners=user) | Q(members=user)
                ).distinct()

            if self.model._meta.model_name == CHANNEL_MODEL_NAME:
                return self.filter(
                    Q(created_by=user) | Q(owners=user)
                ).distinct()

        return self


# Passthrough methods from ProjelQuerySet to ProjelManager
BaseProjelManager = Manager.from_queryset(ProjelQuerySet)


class ProjelManager(BaseProjelManager):
    def get_queryset(self):
        """Only visible Projels."""
        return super(ProjelManager, self).get_queryset().filter(hidden=False)


class UnconfirmedProjelManager(ProjelManager):
    def get_queryset(self):
        """Consider only idea of projects (inside of IdeaStorm)."""
        return super(UnconfirmedProjelManager, self).get_queryset().filter(
            state__in=[states.STATE_IDEA, states.STATE_REJECTED]
        )


class IdeaProjelManager(ProjelManager):
    def get_queryset(self):
        """Consider only idea projects."""
        return super(IdeaProjelManager, self).get_queryset().filter(state=states.STATE_IDEA)


class ActiveProjelManager(ProjelManager):
    def get_queryset(self):
        """Consider only active projects."""
        return super(ActiveProjelManager, self).get_queryset().filter(
            state__in=[states.STATE_ACTIVE, states.STATE_COPY]
        )


class ClosedProjelManager(ProjelManager):
    def get_queryset(self):
        """Consider only closed projects."""
        return super(ClosedProjelManager, self).get_queryset().filter(state=states.STATE_CLOSED)
