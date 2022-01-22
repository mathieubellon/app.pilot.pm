from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0004_init_notifications_token'),
        # The previous migration in app1
        ('items', '0004_rename_filter_models'),
        # This migration should depend on the migration that creates a model in the state of app2,
        # because we are going to refer a new model here.
        ('itemsfilters', '0001_move_filter_models'),
    ]

    state_operations = [
        migrations.AlterField(
            model_name='NotificationFeed',
            name='item_saved_filter',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notification_feeds',
                to='itemsfilters.SavedFilter',
                verbose_name='Saved filter'
            )
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]

