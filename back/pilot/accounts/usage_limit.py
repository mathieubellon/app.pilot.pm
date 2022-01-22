from collections import defaultdict

from django.template.defaultfilters import yesno, filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum

from pilot.accounts.models import NO_USAGE_LIMIT
from pilot.utils import states


class UsageLimitReached(Exception):
    pass


class UsageLimit(object):
    name = None
    label = None
    model_field_name = None
    near_limit_threshold = 3

    # Rudimentary cache, should probably use a real cache
    max_usage_cache = defaultdict(dict)

    @classmethod
    def invalidate_max_usage_cache(cls, desk):
        cls.max_usage_cache.pop(desk.id, None)

    def __init__(self, desk):
        self.desk = desk

    def get_max_usage(self):
        """
        Desk instances are linked to a SubscriptionPlan, and have the limit from the subscription plan.
        But Desk instances can also overrides any limit, in which case the value defined on the desk takes precedence.
        An override on the desk is defined by a non-null value.
        """
        desk_cache = self.max_usage_cache[self.desk.id]

        if self.name not in desk_cache:
            plan = self.desk.subscription_plan
            desk_override = getattr(self.desk, self.model_field_name)
            desk_cache[self.name] = desk_override if desk_override is not None else getattr(plan, self.model_field_name)

        return desk_cache[self.name]

    # Cache to avoid multiple queries
    _current_usage = None
    def get_current_usage(self):
        if self._current_usage is None:
            self._current_usage = self._get_current_usage_impl()
        return self._current_usage

    def _get_current_usage_impl(self):
        raise NotImplementedError()

    def format_usage_value(self, usage_value):
        return _('Illimité') if usage_value == NO_USAGE_LIMIT else self._format_usage_value_impl(usage_value)

    def _format_usage_value_impl(self, usage_value):
        return usage_value

    def format_usage(self):
        return "{} / {}".format(
            self.format_usage_value(self.get_current_usage()),
            self.format_usage_value(self.get_max_usage()),
        )

    def check_limit(self, allow_exact_limit=False):
        max_usage = self.get_max_usage()
        current_usage = self.get_current_usage()
        if max_usage == NO_USAGE_LIMIT:
            return
        # If we allow to be at the exact limit, we should decrease the usage by one
        if allow_exact_limit:
            current_usage -= 1
        if current_usage >= max_usage:
            raise UsageLimitReached(
                _("Limite d'utilisation atteinte:  %(max_usage)s %(label)s") %
                {'max_usage': max_usage, 'label': self.label}
            )

    def is_near_limit(self):
        # If the Usage is unlimited, we're never near the limit
        if self.get_max_usage() == NO_USAGE_LIMIT:
            return False
        return self.usage_left() < self.near_limit_threshold

    def usage_left(self):
        return self.get_max_usage() - self.get_current_usage()

    def get_extra_data(self):
        return {}


class UserUsageLimit(UsageLimit):
    name = 'users'
    label = _('Utilisateurs')
    model_field_name = 'max_users'

    def _get_current_usage_impl(self):
        return self.desk.users.count() \
               + self.desk.invitation_tokens.filter(used=False).count()

    def get_extra_data(self):
        return {
            'invitations': self.desk.invitation_tokens.filter(used=False).count(),
            'users': self.desk.users.count()
        }


class ProjectUsageLimit(UsageLimit):
    name = 'projects'
    label = _('Projets')
    model_field_name = 'max_projects'

    def _get_current_usage_impl(self):
        return self.desk.projects.exclude(state=states.STATE_CLOSED).count()


class ItemUsageLimit(UsageLimit):
    name = 'items'
    label = _('Contenus')
    model_field_name = 'max_items'

    def _get_current_usage_impl(self):
        return self.desk.items.filter(in_trash=False, hidden=False).count()


class AssetStorageUsageLimit(UsageLimit):
    name = 'asset_storage'
    label = _('Stockage maximum')
    model_field_name = 'max_assets_storage'
    near_limit_threshold = 100 * 1024 * 1024 # Threshold at 100 Mb

    def get_max_usage(self):
        """
        In bytes
        """
        return super(AssetStorageUsageLimit, self).get_max_usage() * (1 << 30)

    def _get_current_usage_impl(self):
        """
        In bytes
        """
        storage_used = self.desk.assets.aggregate(Sum('size'))['size__sum']  # In bytes
        if not storage_used:
            return 0
        return storage_used

    def _format_usage_value_impl(self, usage_value):
        return filesizeformat(usage_value)


class AdvancedFeaturesUsageLimit(UsageLimit):
    name = 'advanced_features'
    label = _('Fonctionnalités avancées')
    model_field_name = 'advanced_features'

    def _get_current_usage_impl(self):
        return self.get_max_usage()

    def format_usage_value(self, usage_value):
        return yesno(usage_value)

    def format_usage(self):
        return self.format_usage_value(self.get_max_usage())



ALL_USAGE_LIMITS = (
    UserUsageLimit,
    ProjectUsageLimit,
    ItemUsageLimit,
    AssetStorageUsageLimit,
    AdvancedFeaturesUsageLimit
)


def get_all_usage_limits(desk):
    usage_limits = [UsageLimitImpl(desk) for UsageLimitImpl in ALL_USAGE_LIMITS]

    return [
        {
            'name': usage_limit.name,
            'label': usage_limit.label,
            'max_usage': usage_limit.get_max_usage(),
            'max_usage_display': usage_limit.format_usage_value(usage_limit.get_max_usage()),
            'current_usage': usage_limit.get_current_usage(),
            'current_usage_display': usage_limit.format_usage_value(usage_limit.get_current_usage()),
            'usage_display': usage_limit.format_usage(),
            'is_near_limit': usage_limit.is_near_limit(),
            'usage_left_display': usage_limit.format_usage_value(usage_limit.usage_left()),
            'extra': usage_limit.get_extra_data(),
        }
        for usage_limit in usage_limits
    ]
