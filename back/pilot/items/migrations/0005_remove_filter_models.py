from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0004_rename_filter_models'),
        ('notifications', '0005_update_saved_filter_relation'),
    ]

    state_operations = [
        migrations.DeleteModel('ItemSavedFilter'),
        migrations.DeleteModel('ItemSharedFilter'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]

