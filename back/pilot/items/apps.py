from django.db.models.signals import post_save, m2m_changed
from django.apps import AppConfig


class ItemAppConfig(AppConfig):
    name = 'pilot.items'
    verbose_name = 'Items'

    def ready(self):
        from pilot.items.models import Item
        from pilot.items import signals
        post_save.connect(signals.reindex_item, sender=Item)

        for m2m_field in (Item.targets, Item.assets, Item.owners, Item.tags):
            m2m_changed.connect(signals.reindex_item, sender=m2m_field.through)
