
import arrow

from pilot.items.export_item import ItemXLSExporter
from pilot.items.models import Item
from pilot.pilot_users.models import UserInDesk
from pilot.queue import jobs_registar
from pilot.utils import export_utils


class AllItemsXLSExportJob(export_utils.BaseXLSExportJob):
    """
    Create an xlsx file of all the users of a desk.
    """
    job_type = jobs_registar.JOB_TYPE_ALL_ITEMS_XLS_EXPORT

    def write_data_to_xls_file(self, temp_file):
        desk = self.job_tracker.desk
        user = self.job_tracker.created_by
        user_in_desk = UserInDesk.objects.get(user=user, desk=desk)
        user.set_permissions(user_in_desk.permission, False)

        items = (
            Item.objects
            .filter(desk=desk)
            .filter_by_permissions(user)
            .order_by('id')
            .select_related('project', 'created_by',  'workflow_state')
            .prefetch_related('channels', 'tasks', 'targets', 'owners', 'item_type', 'tags')
        )
        ItemXLSExporter(items, temp_file).do_export()

    def get_file_name(self):
        return "export-pilot-items-{date}.xlsx".format(
            date=arrow.get(self.job_tracker.created_at.isoformat()).format('YYYY-MM-DD')
        )
