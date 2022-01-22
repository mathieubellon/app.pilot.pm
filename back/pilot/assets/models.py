import os
import uuid

from botocore.exceptions import ClientError
from cacheout import memoize

from django.db import models
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.contrib.postgres import fields as pg_fields

from pilot.accounts.usage_limit import AssetStorageUsageLimit
from pilot.desks.models import Desk
from pilot.labels.models import Label
from pilot.notifications.reminders import ReminderImpactorModel
from pilot.utils.alpha import to_alpha
from pilot.utils.models import HideableModel, OptionalCreatorChangeTrackingModel, ChangeTrackingModel
from pilot.utils.prosemirror.prosemirror import prosemirror_json_to_search_document
from pilot.utils.s3 import delete_s3_file, update_s3_filename
from pilot.utils.search import FullTextSearchModel, TrigramIndex


def get_default_conversions():
    return {
        "version": 1,
        "conversionData": {}
    }


class AssetManager(models.Manager):
    def get_queryset(self):
        """Only visible ItemType."""
        return super(AssetManager, self).get_queryset().filter(hidden=False)


class Asset(FullTextSearchModel,
            HideableModel,
            OptionalCreatorChangeTrackingModel):
    """An asset."""

    FILETYPE_CHOICES = (
        ('image', _("Image")),
        ('pdf', _("Pdf")),
        ('video', _("Video")),
        ('audio', _("Audio")),
        ('word', _("Word")),
        ('excel', _("Excel")),
        ('powerpoint', _("Powerpoint")),
        ('autre', _("Autre")),
    )

    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='assets'
    )

    uuid = models.UUIDField(
        primary_key=False,
        default=uuid.uuid4,
        verbose_name='uuid',
        unique=True
    )

    # ===================
    # Content
    # ===================

    title = models.CharField(
        max_length=500,
        verbose_name=_("Titre"),
        db_index=True
    )

    # A rich-text field
    description = pg_fields.JSONField(
        verbose_name=_("Description"),
        default=dict,
        blank=True
    )

    file = models.FileField(
        verbose_name=_("Fichier"),
        upload_to='assets/tmp',
        blank=True
    )

    url = models.URLField(
        verbose_name=_("Lien externe"),
        help_text=_("Vous pouvez saisir un lien vers un fichier"),
        # http://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
        max_length=2000,
        blank=True
    )

    folder = models.ForeignKey(
        Label,
        on_delete=models.SET_NULL,
        verbose_name=_("Dossier"),
        related_name="assets_by_folder",
        blank=True,
        null=True
    )

    # ===================
    # File properties
    # ===================

    size = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    filetype = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Type de fichier"),
        db_index=True
    )

    extension = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Extension")
    )

    mime = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Mime")
    )

    # ===================
    # Transloadit
    # ===================

    conversions = pg_fields.JSONField(
        blank=True,
        null=True,
        default=get_default_conversions,
        verbose_name=_("Conversions"),
    )

    version = models.IntegerField(
        default=1,
        verbose_name="Version"
    )

    # ===================
    # Image fields
    # ===================

    height = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    width = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    html_caption = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Légende ( html )")
    )

    html_title = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Titre ( html )")
    )

    html_alt = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Texte alternatif ( html )")
    )

    # ===================
    # State fields
    # ===================

    is_guideline = models.BooleanField(
        verbose_name=_('Document de référence'),
        default=False
    )

    in_media_library = models.BooleanField(
        default=True,
        db_index=True
    )

    objects = AssetManager()
    all_the_objects = models.Manager()  # for django admin

    class Meta:
        verbose_name = _('Fichier')
        verbose_name_plural = _('Fichiers')
        # Indexes doesn't seems to work on abstract classes ?!?
        # Maybe fixed in a later django release
        indexes = [
            # The index for full-text searches
            GinIndex(fields=['search_vector']),
            TrigramIndex(fields=['partial_search_document'])
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.hidden:
            return None
        return reverse('ui_asset_details', kwargs={'asset_pk': self.pk})

    @memoize(maxsize=1)
    def get_search_values(self):
        return [
            self.title,
            prosemirror_json_to_search_document(self.description)
        ]

    # The name of the asset that we display to the user
    def get_name(self, normalized=False):
        title = to_alpha(self.title) if normalized else self.title
        if self.is_file_asset and self.extension:
            return '{title}.{extension}'.format(
                title=title,
                extension=self.extension
            )
        return title

    @property
    def name(self):
        return self.get_name()

    @property
    def is_file_asset(self):
        return bool(self.file)

    @property
    def pathsep(self):
        if settings.DEFAULT_FILE_STORAGE == 'django.core.files.storage.FileSystemStorage':
            return os.path.sep
        else:
            return '/'

    @property
    def basename(self):
        if self.version == 1:
            # Keep the old name for all existing assets
            return '{0}_{1}'.format(self.desk_id, self.pk)
        else:
            return '{0}_{1}_v{2}'.format(self.desk_id, self.pk, self.version)

    @property
    def basepath(self):
        return 'assets{sep}{deskid}{sep}{assetpk}'.format(
            sep=self.pathsep,
            deskid=self.desk_id,
            assetpk=self.pk
        )

    @property
    def originalpath(self):
        return '{basepath}{sep}{basename}_original{ext}'.format(
            sep=self.pathsep,
            basepath=self.basepath,
            basename=self.basename,
            ext='.{}'.format(self.extension) if self.extension else ''
        )

    @property
    def coverpath(self):
        return '{basepath}{sep}{basename}_cover.jpg'.format(
            sep=self.pathsep,
            basepath=self.basepath,
            basename=self.basename
        )

    @property
    def image_working_path(self):
        return '{basepath}{sep}{basename}_working.jpg'.format(
            sep=self.pathsep,
            basepath=self.basepath,
            basename=self.basename
        )

    @property
    def document_working_path_transloadit(self):
        return '{basepath}{sep}{basename}_working_${{file.basename}}.jpg'.format(
            sep=self.pathsep,
            basepath=self.basepath,
            basename=self.basename
        )

    @property
    def file_url(self):
        try:
            return self.file.url if self.is_file_asset else self.url
        except ValueError:
            # This may happen when the user did not uploaded a file yet
            return ''

    @property
    def cover_url(self):
        return "{s3_base_url}{coverpath}".format(
            s3_base_url=settings.AWS_S3_BASE_URL,
            coverpath=self.coverpath
        )

    @property
    def working_urls(self):
        if not self.conversions:
            return []

        results_key_map = {
            'image': 'workingImage',
            'pdf': 'workingDocument',
            'video': 'workingVideo',
            'audio': 'workingAudio',
        }
        results_key = results_key_map.get(self.filetype.lower())

        # Incorrect format
        if not results_key:
            return []

        conversion_data = self.conversions.get('conversionData', {}).get('results', {})
        conversion_results = conversion_data.get(results_key, [])

        urls = []
        for conversion_result in conversion_results:
            url = conversion_result.get('ssl_url')
            if not url:
                continue
            # See https://gitlab.com/matthieubellon/pilot/issues/814
            # Transloadit build an S3 url that embed the Bucket region as a subdomain.
            # This breaks image loading on some enterprise network (Vinci).
            # We need to build the url manually, without this region subdomain.
            url = settings.AWS_S3_BASE_URL + url.split('/', 3)[-1]
            urls.append(url)
        return urls

    @property
    def conversion_data(self):
        conversions = self.conversions or {}
        return conversions.get('conversionData', {})

    @property
    def is_assembly_completed(self):
        return self.conversion_data.get('ok') == 'ASSEMBLY_COMPLETED'

    @property
    def is_assembly_executing(self):
        return self.conversion_data.get('ok') in ['ASSEMBLY_EXECUTING', 'ASSEMBLY_UPLOADING ']

    @property
    def is_assembly_error(self):
        return 'error' in self.conversion_data

    @property
    def assembly_url(self):
        return self.conversion_data.get('assembly_ssl_url')

    @property
    def is_image(self):
        return self.filetype and self.filetype.lower() == 'image'

    def save(self, *args, **kwargs):
        # In creation, ensure the subscription limit is not reached
        if not self.pk:
            AssetStorageUsageLimit(self.desk).check_limit()

            if not self.html_title:
                self.html_title = self.title
            if not self.html_alt:
                self.html_alt = self.title

        super(Asset, self).save(*args, **kwargs)
        # When working with the file system,
        # move the file from the tmp dir to its final dir
        # once the Asset's pk is assigned.
        if (self.file and
           settings.DEFAULT_FILE_STORAGE == 'django.core.files.storage.FileSystemStorage' and 'tmp' in self.file.path):
            old_path = os.path.join(settings.MEDIA_ROOT, self.file.path)
            new_path = os.path.join(settings.MEDIA_ROOT, self.originalpath)
            os.renames(old_path, new_path)
            self.file = new_path
            super(Asset, self).save(*args, **kwargs)

    def update_s3_filename(self):
        try:
            update_s3_filename(self.originalpath, self.get_name(normalized=True))
        except ClientError as e:
            # We may have a copy error when the original file does not exists.
            # It may not exists because some old files were saved with an upper case extensions.
            # We retry by upcasing the extension.
            if e.response.get('Error', {}).get('Code') == 'NoSuchKey' and '.' in self.originalpath:
                base_path, ext = self.originalpath.split('.')
                upped_path = base_path + '.' + ext.upper()
                update_s3_filename(upped_path, self.get_name(normalized=True))
            else:
                raise

    def update_conversion_data(self, conversion_data):
        self.conversions['conversionData'] = conversion_data

        if self.is_assembly_completed:
            original = conversion_data['results']['original'][0]

            self.size = original['size']
            self.mime = original['mime']
            if original['ext'] != '':
                self.extension = original['ext']

            if original['type']:
                self.filetype = original['type']
            elif self.extension == 'docx' or self.extension == 'doc':
                self.filetype = 'word'
                self.width = None
                self.height = None
            elif self.extension == 'xlsx' or self.extension == 'xls':
                self.filetype = 'excel'
                self.width = None
                self.height = None
            elif self.extension == 'pptx' or self.extension == 'ppt':
                self.filetype = 'powerpoint'
                self.width = None
                self.height = None
            else:
                self.filetype = 'autre'
                self.width = None
                self.height = None

            if self.filetype == 'image' or self.filetype == 'video':
                self.width = original['meta']['width']
                self.height = original['meta']['height']

    def delete_s3_files(self):
        delete_s3_file(self.originalpath)
        delete_s3_file(self.coverpath)

        for working_url in self.working_urls:
            delete_s3_file(working_url.split('/', 3)[-1])


class AssetRight(ChangeTrackingModel,
                 ReminderImpactorModel):
    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        verbose_name=_("Desk"),
        related_name='asset_rights'
    )

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        verbose_name=_("Fichier"),
        related_name='asset_rights'
    )

    medium = models.ForeignKey(
        Label,
        on_delete=models.SET_NULL,
        verbose_name=_("Support de communication"),
        related_name="asset_rights_by_medium",
        blank=True,
        null=True,
    )

    expiry = models.DateField(
        verbose_name=_("Date d'expiration"),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Droit d'utilisation de média")
        ordering = ('expiry',)

    def __str__(self):
        return _("Droit d'utilisation de {}").format(self.asset)

    def get_absolute_url(self):
        return self.asset.get_absolute_url() + '/usageRights'
