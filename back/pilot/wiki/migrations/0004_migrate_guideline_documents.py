# Generated by Django 2.2.14 on 2020-11-24 14:47
from django.db import migrations
from django.utils import timezone

from pilot.utils import noop
from pilot.utils.prosemirror.prosemirror import EMPTY_PROSEMIRROR_DOC


def migrate_guideline_documents(apps, schema_editor):
    Asset = apps.get_model('assets', 'Asset')
    WikiPage = apps.get_model('wiki', 'WikiPage')

    for asset in Asset.objects.filter(is_guideline=True).exclude(hidden=True):
        wiki_page = WikiPage.objects.create(
            desk=asset.desk,
            created_by_id=1,
            updated_at=timezone.now(),
            name=asset.title,
            is_home_page=False,
            content=EMPTY_PROSEMIRROR_DOC
        )
        wiki_page.assets.add(asset)


class Migration(migrations.Migration):

    dependencies = [
        ('wiki', '0003_wikipage_assets'),
    ]

    operations = [
        migrations.RunPython(migrate_guideline_documents, noop),
    ]
