from django.utils.translation import ugettext_lazy as _


JOB_TYPE_ALL_ITEMS_XLS_EXPORT = 'all_items_xls_export'
JOB_TYPE_ALL_PROJECTS_XLS_EXPORT = 'all_projects_xls_export'
JOB_TYPE_ALL_USERS_XLS_EXPORT = 'all_users_xls_export'
JOB_TYPE_ASSET_EXPORT = 'asset_export'
JOB_TYPE_COPY_PROJECT = 'copy_project'
JOB_TYPE_DESK_EXPORT = 'desk_export'
JOB_TYPE_HIERARCHY_CONSISTENCY = 'hierarchy_consistency'
JOB_TYPE_ITEM_TYPE_UPDATE = 'item_type_update'
JOB_TYPE_MENTION_UPDATE = 'mention_update'
JOB_TYPE_NOTIFY = 'notify'
JOB_TYPE_SAVED_FILTER_EXPORT = 'saved_filter_export'

JOB_TYPE_CHOICES = (
    (JOB_TYPE_ALL_ITEMS_XLS_EXPORT, _("All Items XLS Export")),
    (JOB_TYPE_ALL_PROJECTS_XLS_EXPORT, _("All Projects XLS Export")),
    (JOB_TYPE_ALL_USERS_XLS_EXPORT, _("All Users XLS Export")),
    (JOB_TYPE_ASSET_EXPORT, _("Asset Export")),
    (JOB_TYPE_COPY_PROJECT, _("Copy Project")),
    (JOB_TYPE_DESK_EXPORT, _("Desk Export")),
    (JOB_TYPE_HIERARCHY_CONSISTENCY, _("Hierarchy consistency")),
    (JOB_TYPE_ITEM_TYPE_UPDATE, _("Item Type Update")),
    (JOB_TYPE_MENTION_UPDATE, _("Mention Update")),
    (JOB_TYPE_NOTIFY,  _("Notify")),
    (JOB_TYPE_SAVED_FILTER_EXPORT, _("Saved Filter Export")),
)


def get_all_jobs():
    from pilot.comments.jobs import MentionUpdateJob
    from pilot.desks.jobs import AssetExportJob
    from pilot.desks.jobs import DeskExportFinalizeJob
    from pilot.item_types.jobs import ItemTypeUpdateJob
    from pilot.items.jobs import AllItemsXLSExportJob
    from pilot.itemsfilters.jobs import ItemFilterXLSExportJob
    from pilot.notifications.jobs import NotifyJob
    from pilot.pilot_users.jobs import AllUsersXLSExportJob
    from pilot.projects.jobs import AllProjectsXLSExportJob
    from pilot.projects.jobs import CopyProjectJob
    from pilot.utils.projel.hierarchy import HierarchyConsistencyJob

    return [
        AllItemsXLSExportJob,
        AllProjectsXLSExportJob,
        AllUsersXLSExportJob,
        AssetExportJob,
        CopyProjectJob,
        DeskExportFinalizeJob,
        HierarchyConsistencyJob,
        ItemFilterXLSExportJob,
        ItemTypeUpdateJob,
        MentionUpdateJob,
        NotifyJob
    ]


def get_job_by_type(job_type):
    all_jobs_by_type = {job_class.job_type: job_class for job_class in get_all_jobs()}
    return all_jobs_by_type[job_type]
