from django.db import migrations, models

class Migration(migrations.Migration):

    replaces = [('accounts', '0001_initial'), ('accounts', '0002_init_subscription_plans')]

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_users', models.IntegerField(blank=True, null=True, verbose_name="Nombre maximum d'utilisateurs")),
                ('max_projects', models.IntegerField(blank=True, null=True, verbose_name='Nombre maximum de projets')),
                ('max_items', models.IntegerField(blank=True, null=True, verbose_name='Nombre maximum de contenus')),
                ('max_assets_storage', models.IntegerField(blank=True, null=True, verbose_name='Taille de stockage maximale (en Giga-octets)')),
                ('advanced_features', models.NullBooleanField(verbose_name='Accès aux fonctionnalités avancées ?')),
                ('name', models.CharField(max_length=200, verbose_name='Nom')),
                ('display_price', models.CharField(blank=True, help_text="Valeur d'affichage uniquement, aucun impact sur la facturation réelle.Seule la configuration Stripe impacte la prix facturé.", max_length=100, verbose_name='Prix affiché')),
                ('stripe_plan_id', models.CharField(max_length=50, verbose_name='Stripe plan id')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
