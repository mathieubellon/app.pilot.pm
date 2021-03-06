# Generated by Django 2.1.7 on 2019-02-14 10:28

from django.conf import settings
import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import pilot.utils.search


class Migration(migrations.Migration):

    replaces = [('projects', '0001_initial'), ('projects', '0002_campaign_color'), ('projects', '0003_auto_20151116_2137'), ('projects', '0004_auto_20151116_2139'), ('projects', '0005_remove_campaign_owner'), ('projects', '0006_auto_20160331_1307'), ('projects', '0007_campaign_priority'), ('projects', '0008_auto_20170623_1517'), ('projects', '0009_campaign_label'), ('projects', '0010_auto_20170627_1531'), ('projects', '0011_init_search_vector_field'), ('projects', '0012_init_search_vector_index'), ('projects', '0013_init_partial_search_document_field'), ('projects', '0014_init_partial_search_document_index'), ('projects', '0015_auto_20171127_1047'), ('projects', '0016_remove_campaign_name_alpha'), ('projects', '0017_remove_time_from_start_end'), ('projects', '0018_auto_20180423_1724'), ('projects', '0019_auto_20180424_1741'), ('projects', '0020_remove_project_slug'), ('projects', '0021_auto_20181113_1053'), ('projects', '0022_project_new_tags'), ('projects', '0023_auto_20181129_1108'), ('projects', '0024_project_new_priority'), ('projects', '0025_migrate_project_priority'), ('projects', '0026_auto_20181204_1102'), ('projects', '0027_migrate_project_color'), ('projects', '0028_auto_20181213_1700'), ('projects', '0029_auto_20190114_0950')]

    initial = True

    dependencies = [
        ('targets', '0001_rebirth'),
        ('labels', '0001_rebirth'),
        ('channels', '0001_rebirth'),
        ('assets', '0001_rebirth'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('desks', '0001_rebirth'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(blank=True, verbose_name='Mis ?? jour ??')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Cr???? le')),
                ('search_vector', django.contrib.postgres.search.SearchVectorField(null=True)),
                ('partial_search_document', models.TextField(blank=True)),
                ('name', models.CharField(max_length=200, verbose_name='Nom')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('start', models.DateField(blank=True, db_index=True, null=True, verbose_name='Date de d??but')),
                ('end', models.DateField(blank=True, db_index=True, null=True, verbose_name='Date de fin')),
                ('state', models.CharField(choices=[('idea', 'Proposition'), ('rejected', 'Rejet??'), ('active', 'Actif'), ('closed', 'Ferm??'), ('copy', 'En cours de copie')], db_index=True, default='idea', max_length=16, verbose_name='Statut')),
                ('hidden', models.BooleanField(default=False, verbose_name='Invisible')),
                ('closed_at', models.DateTimeField(blank=True, null=True, verbose_name='Ferm?? le')),
                ('created_by_external_email', models.EmailField(blank=True, db_index=True, max_length=254, verbose_name='Cr???? par contact externe')),
                ('created_by_external_token', models.CharField(blank=True, max_length=255, verbose_name='Cr???? par token externe')),
                ('assets', models.ManyToManyField(blank=True, related_name='projects', to='assets.Asset', verbose_name='M??dias')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects_by_category', to='labels.Label', verbose_name='Categorie')),
                ('channels', models.ManyToManyField(blank=True, related_name='projects', to='channels.Channel', verbose_name='Canaux')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_created', to=settings.AUTH_USER_MODEL, verbose_name='Cr???? par')),
                ('desk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='desks.Desk', verbose_name='Desk')),
                ('owners', models.ManyToManyField(blank=True, related_name='projects_owned_by', to=settings.AUTH_USER_MODEL, verbose_name='Responsables')),
                ('priority', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects_by_priority', to='labels.Label', verbose_name='Priorit??')),
                ('tags', models.ManyToManyField(related_name='projects_by_tags', to='labels.Label', verbose_name='Tags')),
                ('targets', models.ManyToManyField(blank=True, related_name='projects', to='targets.Target', verbose_name='Cibles')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='project_updated', to=settings.AUTH_USER_MODEL, verbose_name='Mis ?? jour par')),
            ],
            options={
                'verbose_name': 'Projet',
                'verbose_name_plural': 'Projets',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='project',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_vector'], name='projects_pr_search__1d35f9_gin'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=pilot.utils.search.TrigramIndex(fields=['partial_search_document'], name='projects_pr_partial_4f3f4c_gin'),
        ),
    ]
