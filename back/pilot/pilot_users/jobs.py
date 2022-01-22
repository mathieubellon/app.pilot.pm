
import arrow

from django.db.models import Prefetch

from pilot.pilot_users.models import PilotUser, Team
from pilot.queue import jobs_registar
from pilot.utils import export_utils


class UserXLSExporter(export_utils.BaseXLSExporter):
    model = PilotUser
    metadata_fields = export_utils.USER_METADATA_FIELDS


class AllUsersXLSExportJob(export_utils.BaseXLSExportJob):
    """
    Create an xlsx file of all the users of a desk.
    """
    job_type = jobs_registar.JOB_TYPE_ALL_USERS_XLS_EXPORT

    def write_data_to_xls_file(self, temp_file):
        users = (PilotUser.objects
                 .filter(desks=self.job_tracker.desk).order_by('id')
                 # VERY IMPORTANT : Filter the teams to keep only those of the current desk.
                 # ALso optimize by prefeteching the M2M relationship.
                 .prefetch_related(Prefetch('teams', queryset=Team.objects.filter(desk=self.job_tracker.desk))))
        UserXLSExporter(users, temp_file).do_export()

    def get_file_name(self):
        return "export-pilot-users-{date}.xlsx".format(
            date=arrow.get(self.job_tracker.created_at.isoformat()).format('YYYY-MM-DD')
        )
