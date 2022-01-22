import hashlib
import tempfile
import threading
import zipfile
import logging
from collections import OrderedDict

import arrow

from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

from pilot.activity_stream.comment import get_comments_queryset
from pilot.assets.models import Asset
from pilot.items.export_item import ItemContentExporter
from pilot.items.models import Item
from pilot.notifications.const import NotificationType
from pilot.notifications.notify import notify
from pilot.projects.models import Project
from pilot.queue.jobs import Job, SelfCleaningThreadPool
from pilot.queue import jobs_registar
from pilot.queue.rq_setup import low_priority_queue
from pilot.utils import export_utils
from pilot.utils.alpha import to_alpha
from pilot.utils.prosemirror.prosemirror import prosemirror_json_to_html
from pilot.utils.s3 import upload_s3_file_multipart, download_s3_file, s3_file_exists
from pilot.utils.stream_zipfile import BufferedZipFile

logger = logging.getLogger(__name__)

MAX_FILE_NAME_LENGTH = 80
THREAD_POOL_SIZE = 20
THREAD_POOL_SIZE_ASSET_DOWNLOAD = 2


def launch_desk_export(request):
    previous_asset_export_job = None
    for year in get_years_since_desk_creation(request.desk):
        asset_launch = AssetExportJob.launch_r(
            request,
            year,
            depends_on=previous_asset_export_job,
            timeout='1h',
        )
        previous_asset_export_job = asset_launch['job_id']

    launch = DeskExportFinalizeJob.launch_r(
        request,
        depends_on=previous_asset_export_job,
        timeout='1h'
    )

    return launch


def format_file_name(base_name):
    file_name = to_alpha(base_name, to_lower=False)
    if len(file_name) > MAX_FILE_NAME_LENGTH:
        file_name = file_name[0:MAX_FILE_NAME_LENGTH]
    return file_name


def get_years_since_desk_creation(desk):
    return range(desk.created_at.date().year, arrow.now().year + 1)


def annual_asset_zip_name(year):
    return "assets_{}.zip".format(year)


def annual_asset_zip_s3_key(desk, year):
    year_hash = hashlib.sha1("{}{}".format(year, settings.SECRET_KEY).encode()).hexdigest()[:10]
    return 'export/{deskId}/assets_{year}_{hash}.zip'.format(
        deskId=desk.id,
        year=year,
        hash=year_hash
    )


def get_asset_paths(asset):
    format_kwargs = dict(
        id=asset.id,
        name=format_file_name(asset.title),
        year=asset.created_at.year,
        normalized_name=asset.get_name(normalized=True)
    )

    return {
        'file_path': "files/{year}/{id}-{normalized_name}".format(**format_kwargs),
        'metadata_path': "assets/{id}-{name}/{name}-metadata.html".format(**format_kwargs),
        'index_path': "assets/{id}-{name}/index.html".format(**format_kwargs)
    }


class BaseExport(object):
    def __init__(self, *args, **kwargs):
        super(BaseExport, self).__init__(*args, **kwargs)
        self.zip_write_lock = threading.Lock()
        self.zip_file = None
        self.temp_file = None

    def open_zip_file(self):
        self.temp_file = tempfile.NamedTemporaryFile()
        self.zip_file = BufferedZipFile(self.temp_file, mode='w', compression=zipfile.ZIP_DEFLATED)

    def finalize_and_upload_zip_file(self, s3_key, file_name):
        # Finalize the zip archive
        self.zip_file.close()
        # Rewind the temporary file storage to the beginning
        self.temp_file.seek(0)
        # Upload the archive to S3
        upload_s3_file_multipart(s3_key, self.temp_file.file, file_name)
        # Close the temporary file
        self.temp_file.close()

    def thread_safe_write_to_zip(self, file_path, file, is_stream=False):
        self.zip_write_lock.acquire()
        if is_stream:
            self.zip_file.write_s3_streaming_body(file_path, file)
        else:
            self.zip_file.writestr(file_path, file)
        self.zip_write_lock.release()

    def export_metadata(self, instance, metadata_path, metadata_fields):
        metadata_list = [
            {
                'label': instance._meta.get_field(metadata_field_name).verbose_name,
                'value': export_utils.format_field(instance, metadata_field_name)
            }
            for metadata_field_name in metadata_fields
        ]

        metadata_file = render_to_string("desk_export/metadata.html", {
            'instance': instance,
            'metadata_list': metadata_list
        })
        self.thread_safe_write_to_zip(metadata_path, metadata_file.encode())


class AssetExportJob(BaseExport, Job):
    job_type = jobs_registar.JOB_TYPE_ASSET_EXPORT
    queue = low_priority_queue

    def run(self, year):
        s3_key = annual_asset_zip_s3_key(self.job_tracker.desk, year)

        # The asset zip already exists, and is not the current year, don't generate it again
        if s3_file_exists(s3_key) and year != arrow.now().year:
            return

        self.year = year

        self.open_zip_file()

        self.export_assets_for_year()

        # Finalize and upload the zip archive
        file_name = annual_asset_zip_name(year)
        self.finalize_and_upload_zip_file(s3_key, file_name)

    def export_assets_for_year(self):
        # Use a thread pool for I/O bound operations (db connections & AWS connections )
        thread_pool = SelfCleaningThreadPool(THREAD_POOL_SIZE_ASSET_DOWNLOAD)

        # Iterate only on assets which have an actual file associated (exclude UrlAsset)
        for asset in (Asset.objects
            .filter(desk=self.job_tracker.desk)
            .filter(created_at__year=self.year)
            .exclude(file="")
            .order_by('-id')
            .iterator()
        ):
            thread_pool.apply_async(self.export_one_asset, [asset])

        thread_pool.close()
        thread_pool.join()

    def export_one_asset(self, asset):
        try:
            asset_paths = get_asset_paths(asset)

            # Asset file
            file_path = asset_paths['file_path']
            s3_file_stream = download_s3_file(asset.originalpath)

            # Here we directly push the S3 file stream into the zipfile.
            # This is not optimized at all, because only one thread at a time can write to the zip file.
            # But we need to limit our RAM usage because the Heroku worker have a low RAM usage limit.
            # If we let 20 threads load all the stream into the RAM, we would quickly exceed our 500Mo limit.
            self.thread_safe_write_to_zip(file_path, s3_file_stream, is_stream=True)

            # Here we do not directly push the stream into the zipfile.
            # Instead, all threads download concurrently their file data in-memory,
            # then write the data from the memory to the temp file, which is much faster.
            # self.thread_safe_write_to_zip(file_path, s3_file_stream.read(), is_stream=False)
        except:
            logger.error("[AssetExportJob Error]\nAsset ID : {}".format(asset.id), exc_info=True)
            raise


class DeskExportFinalizeJob(BaseExport, Job):
    """
    Create an archive file of all the data pertaining to a desk.

    This job heavily use tasks that are I/O bound : db calls and S3 downloads.
    We use a ThreadPool to efficiently add concurrency around those I/O bound operations.
    """
    job_type = jobs_registar.JOB_TYPE_DESK_EXPORT
    queue = low_priority_queue

    download_export_string = export_utils.BaseXLSExportJob.download_export_string
    email_subject = export_utils.BaseXLSExportJob.email_subject
    notification_message = export_utils.BaseXLSExportJob.notification_message

    def run(self, bundle_assets=True):
        self.index_files = {
            'assets': OrderedDict(),
            'projects': OrderedDict(),
            'items': OrderedDict()
        }

        self.open_zip_file()

        # The order here is important :
        # The items need their linkedAssets
        # Then the project need their linkedItems & linkedAssets
        self.export_assets()
        self.export_items()
        self.export_projects()

        if bundle_assets:
            for year in get_years_since_desk_creation(self.job_tracker.desk):
                asset_zip_name = annual_asset_zip_name(year)
                s3_zip_streamed = download_s3_file(annual_asset_zip_s3_key(self.job_tracker.desk, year))
                self.thread_safe_write_to_zip(asset_zip_name, s3_zip_streamed, is_stream=True)

        # Main index file
        main_index = render_to_string("desk_export/index.html", {
            'index_files': self.index_files
        })
        self.zip_file.writestr("index.html", main_index.encode())

        s3_key = 'export/{deskId}/{uuid}'.format(
            deskId=self.job_tracker.desk.id,
            uuid=self.job_tracker.job_id
        )
        file_name = "export-pilot-{date}.zip".format(
            date=arrow.get(self.job_tracker.created_at.isoformat()).format('YYYY-MM-DD')
        )

        # Finalize and upload the zip archive
        self.finalize_and_upload_zip_file(s3_key, file_name)

        # Save the result in the JobTracker
        self.job_tracker.data = {
            'result_file_name': file_name,
            'result_url': settings.AWS_S3_BASE_URL + s3_key
        }
        self.job_tracker.save()
        # Notify the user that the export is finished
        self.notify_desk_export_completed()

    def export_assets(self):
        # Use a thread pool for I/O bound operations (db connections & AWS connections )
        thread_pool = SelfCleaningThreadPool(THREAD_POOL_SIZE)

        # Iterate only on assets which have an actual file associated (exclude UrlAsset)
        for asset in (Asset.objects
            .filter(desk=self.job_tracker.desk)
            .exclude(file=None)
            .order_by('-id')
            .select_related(
                'created_by',
                'updated_by'
            )
            .iterator()
        ):
            thread_pool.apply_async(self.export_one_asset, [asset])

        thread_pool.close()
        thread_pool.join()

    def export_one_asset(self, asset):
        try:
            asset_paths = get_asset_paths(asset)

            # Asset metadata in html
            metadata_path = asset_paths['metadata_path']
            self.export_metadata(asset, metadata_path, export_utils.ASSET_METADATA_FIELDS)

            # Index file
            index_path = asset_paths['index_path']
            index_file = render_to_string("desk_export/asset_index.html", {
                'asset': asset,
                'file_path': asset_paths['file_path'],
                'metadata_path': metadata_path
            })
            self.thread_safe_write_to_zip(index_path, index_file.encode())
            self.index_files['assets'][asset.id] = {
                'path': index_path,
                'name': asset.name
            }
        except:
            logger.error("[DeskExportFinalizeJob Error]\nAsset ID : {}".format(asset.id), exc_info=True)
            raise

    def export_projects(self):
        # Use a thread pool for I/O bound operations (db connections & AWS connections )
        thread_pool = SelfCleaningThreadPool(THREAD_POOL_SIZE)

        for project in (Project.objects
            .filter(desk=self.job_tracker.desk)
            .order_by('-id')
            .select_related(
                'category',
                'created_by',
                'updated_by',
            )
            .prefetch_related(
                'channels',
                'owners',
                'targets',
            )
            .iterator()
        ):
            thread_pool.apply_async(self.export_one_project, [project])

        thread_pool.close()
        thread_pool.join()

    def export_one_project(self, project):
        try:
            format_kwargs = dict(
                id=project.id,
                name=format_file_name(project.name)
            )
            path = 'projects/{id}-{name}'.format(**format_kwargs)
            format_kwargs['path'] = path

            assets_ids = project.assets.values_list('id', flat=True)
            assets_export = '\n'.join([str(id) for id in assets_ids])

            items_ids = project.items.values_list('id', flat=True)
            items_export = '\n'.join([str(id) for id in items_ids])

            # Project metadata in html
            metadata_path = "{path}/{name}-metadata.html".format(**format_kwargs)
            self.export_metadata(project, metadata_path, export_utils.PROJECT_METADATA_FIELDS)
            # Linked assets
            self.thread_safe_write_to_zip("{path}/linkedAssets.txt".format(**format_kwargs), assets_export)
            # Linked items
            self.thread_safe_write_to_zip("{path}/linkedItems.txt".format(**format_kwargs), items_export)

            # Index file
            index_path = "{path}/index.html".format(**format_kwargs)
            linked_assets_indicies = [self.index_files['assets'].get(asset_id) for asset_id in assets_ids]
            linked_items_indicies = [self.index_files['items'].get(item_id) for item_id in items_ids]
            index_file = render_to_string("desk_export/project_index.html", {
                'project': project,
                'metadata_path': metadata_path,
                'linked_assets_indicies': linked_assets_indicies,
                'linked_items_indicies': linked_items_indicies
            })
            self.thread_safe_write_to_zip(index_path, index_file.encode())
            self.index_files['projects'][project.id] = {
                'path': index_path,
                'name': "#{} {}".format(project.id, project.name)
            }
        except:
            logger.error("[DeskExportFinalizeJob Error]\nProject ID : {}".format(project.id), exc_info=True)
            raise

    def export_items(self):
        # Use a thread pool for I/O bound operations (db connections & AWS connections )
        thread_pool = SelfCleaningThreadPool(THREAD_POOL_SIZE)

        for item in (Item.objects
            .filter(desk=self.job_tracker.desk)
            .order_by('-id')
            .select_related(
                'workflow_state',
                'created_by',
                'updated_by',
            )
            .prefetch_related(
                'channels',
                'owners',
                'targets',
            )
            .iterator()
        ):
            thread_pool.apply_async(self.export_one_item, [item])

        thread_pool.close()
        thread_pool.join()

    def export_one_item(self, item):
        try:
            format_kwargs = dict(
                id=item.id,
                name=format_file_name(item.title)
            )
            path = 'items/{id}-{name}'.format(**format_kwargs)
            format_kwargs['path'] = path

            item_exporter = ItemContentExporter(item)
            assets_ids = item.assets.values_list('id', flat=True)
            assets_export = '\n'.join([str(id) for id in assets_ids])

            # Item content in html
            html_content_path = "{path}/{name}.html".format(**format_kwargs)
            self.thread_safe_write_to_zip(html_content_path, item_exporter.export_to_html().encode())
            # Item content in docx
            docx_content_path = "{path}/{name}.docx".format(**format_kwargs)
            self.thread_safe_write_to_zip(docx_content_path, item_exporter.export_to_docx())
            # Item metadata in html
            metadata_path = "{path}/{name}-metadata.html".format(**format_kwargs)
            self.export_metadata(item, metadata_path, export_utils.ITEM_METADATA_FIELDS)
            # Comments
            comments_path = "{path}/{name}-comments.html".format(**format_kwargs)
            self.thread_safe_write_to_zip(comments_path, self.export_item_comments(item).encode())
            # Linked assets
            self.thread_safe_write_to_zip("{path}/linkedAssets.txt".format(**format_kwargs), assets_export)


            # Index file
            index_path = "{path}/index.html".format(**format_kwargs)
            linked_assets_indicies = [self.index_files['assets'].get(asset_id) for asset_id in assets_ids]
            index_file = render_to_string("desk_export/item_index.html", {
                'item': item,
                'html_content_path': html_content_path,
                'docx_content_path': docx_content_path,
                'metadata_path': metadata_path,
                'comments_path': comments_path,
                'linked_assets_indicies': linked_assets_indicies
            })
            self.thread_safe_write_to_zip(index_path, index_file.encode())
            self.index_files['items'][item.id] = {
                'path': index_path,
                'name': "#{} {}".format(item.id, item.title)
            }
        except:
            logger.error("[DeskExportFinalizeJob Error]\nItem ID : {}".format(item.id), exc_info=True)
            raise

    def export_item_comments(self, item):
        comments = get_comments_queryset(item)

        output_data = ''
        for comment in comments:
            output_data += "Le {} par {} à propos de la {}".format(
                comment.submit_date.strftime('%Y/%m/%d %H:%M:%S'),
                comment.user.username,
                comment.data.get('version', 'v?')
            )
            output_data += '<br/>'
            output_data += prosemirror_json_to_html(comment.comment_content)
            output_data += '<br/><br/><br/>'

        return output_data

    def notify_desk_export_completed(self):
        notify(
            desk=self.job_tracker.desk,
            type=NotificationType.EXPORT_DESK,
            to_users=[self.job_tracker.created_by],
            message=self.notification_message,
            email_subject=self.email_subject,
            target_url=reverse('ui_desk_export'),
            button_action_text=self.download_export_string,
            data=self.get_notification_data(),
            context=self.get_notification_context(),
        )

    def get_notification_context(self):
        return {
            'export_url': self.job_tracker.data['result_url'],
        }

    def get_notification_data(self):
        return {
            'export_type': self.job_type
        }
