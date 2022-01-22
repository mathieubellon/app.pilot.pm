
import arrow
from django.utils.encoding import force_text

from django.utils.translation import ugettext_lazy as _

from pilot.itemsfilters.saved_filter import export_saved_filter_to_xls
from pilot.queue import jobs_registar
from pilot.utils import export_utils
from pilot.utils.api.generic import GLOSavedFilterSerializer


class ItemFilterXLSExportJob(export_utils.BaseXLSExportJob):
    """
    Create an xlsx file of all the items inside a saved filter.
    """
    job_type = jobs_registar.JOB_TYPE_SAVED_FILTER_EXPORT
    email_subject = _("Export de filtre terminé")
    notification_message = _("L'export du filtre {saved_filter.title} que vous avez demandé est terminé. "
                             "<a href='{export_url}'>Cliquez ici pour le télécharger</a>")

    def run(self, saved_filter):
        self.saved_filter = saved_filter
        self.run_export()

    def write_data_to_xls_file(self, temp_file):
        export_saved_filter_to_xls(self.saved_filter, temp_file)

    def get_file_name(self):
        return "export-pilot-filter-{id}-{date}.xlsx".format(
            id=self.saved_filter.id,
            date=arrow.get(self.job_tracker.created_at.isoformat()).format('YYYY-MM-DD')
        )

    def get_notification_context(self):
        return {
            'export_url': self.job_tracker.data['result_url'],
            'saved_filter': self.saved_filter,
        }

    def get_notification_data(self):
        return {
            'title': force_text(self.download_export_string),
            'export_type': self.job_type,
            'saved_filter': GLOSavedFilterSerializer(self.saved_filter).data,
        }
