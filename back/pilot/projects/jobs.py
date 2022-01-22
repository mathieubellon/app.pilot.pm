import arrow

from django.utils.translation import ugettext_lazy as _

from pilot.notifications.const import NotificationType
from pilot.pilot_users.models import UserInDesk
from pilot.projects.models import Project
from pilot.queue.jobs import Job
from pilot.queue import jobs_registar
from pilot.queue.rq_setup import medium_priority_queue
from pilot.notifications.notify import notify
from pilot.utils import export_utils
from pilot.utils.copy_utils import copy_project


class CopyProjectJob(Job):
    """
    A job that copy a project into a new project,
    then create a corresponding activity, and notify the user of the copy completion.
    """
    job_type = jobs_registar.JOB_TYPE_COPY_PROJECT
    queue = medium_priority_queue

    def run(self, source_project, new_project, copy_params={}):
        copy_project(source_project, new_project, copy_params)

        # Notify the user that the copy is finished
        self.notify_copy_completed(source_project, new_project)

    def notify_copy_completed(self, source_project, new_project):
        notify(
            desk=new_project.desk,
            type=NotificationType.COPY_PROJECT,
            to_users=[new_project.created_by],
            message=_('La copie du projet "{source_project}" que vous avez demandé est terminée'),
            email_subject=_("Copie de projet terminée"),
            linked_object=new_project,
            button_action_text=_("Voir le projet"),
            context={
                'source_project': source_project
            }
        )


class ProjectXLSExporter(export_utils.BaseXLSExporter):
    model = Project
    metadata_fields = export_utils.PROJECT_METADATA_FIELDS

    def get_header(self):
        # 1/ Metadata fields
        yield from super(ProjectXLSExporter, self).get_header()

        # 2/ Content count
        yield _('Nombre de contenus')

    def get_row(self, i, project):
        # 1/ Metadata fields
        yield from super(ProjectXLSExporter, self).get_row(i, project)

        # 2/ Content count
        yield project.items.count()

    def add_style(self):
        super(ProjectXLSExporter, self).add_style()

        # Decrease the width of the id column
        self.worksheet.column_dimensions['A'].width = 10


class AllProjectsXLSExportJob(export_utils.BaseXLSExportJob):
    """
    Create an xlsx file of all the users of a desk.
    """
    job_type = jobs_registar.JOB_TYPE_ALL_PROJECTS_XLS_EXPORT

    def write_data_to_xls_file(self, temp_file):
        desk = self.job_tracker.desk
        user = self.job_tracker.created_by
        user_in_desk = UserInDesk.objects.get(user=user, desk=desk)
        user.set_permissions(user_in_desk.permission, False)

        projects = (
            Project.objects
            .filter(desk=desk)
            .filter_by_permissions(user)
            .order_by('id')
            .select_related('created_by', 'updated_by', 'category', 'priority')
            .prefetch_related('channels', 'owners', 'targets', 'tags')
            .distinct()
        )
        ProjectXLSExporter(projects, temp_file).do_export()

    def get_file_name(self):
        return "export-pilot-projects-{date}.xlsx".format(
            date=arrow.get(self.job_tracker.created_at.isoformat()).format('YYYY-MM-DD')
        )
