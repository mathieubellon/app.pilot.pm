from django.db.models.signals import post_save, m2m_changed
from django.apps import AppConfig


class ProjectAppConfig(AppConfig):
    name = 'pilot.projects'
    verbose_name = 'Projects'

    def ready(self):
        from pilot.projects.models import Project
        from pilot.projects import signals
        post_save.connect(signals.reindex_project, sender=Project)

        for m2m_field in (Project.targets, Project.channels, Project.tags):
            m2m_changed.connect(signals.reindex_project, sender=m2m_field.through)
