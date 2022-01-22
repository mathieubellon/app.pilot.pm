import json
import hashlib
import hmac
import os
from threading import Timer

import requests
from datetime import datetime, timedelta

from django.conf import settings
from django.urls import reverse

from pilot.assets.api.serializers import AssetSerializer
from pilot.realtime.broadcasting import broadcaster
from pilot.utils.url import get_fully_qualified_url
from pilot.assets.models import Asset


ASSEMBLY_API_URL = 'http://api2.transloadit.com/assemblies'


class TransloaditClient(object):
    def __init__(self, key, secret, api=None):
        self.key = key
        if isinstance(secret, str):
            secret = secret.encode()
        self.secret = secret
        if api:
            self.api = api
        else:
            self.api = ASSEMBLY_API_URL

    def _sign_request(self, params):
        return hmac.new(
            self.secret,
            json.dumps(params).encode(),
            hashlib.sha1
        ).hexdigest()

    def request(self, files=None, **params):
        if 'auth' not in params:
            params['auth'] = {
                'key': self.key,
                'expires': (datetime.now() + timedelta(days=1)).strftime('%Y/%m/%d %H:%M:%S')
            }

        response = requests.post(
            ASSEMBLY_API_URL,
            data={
                'params': json.dumps(params),
                'signature': self._sign_request(params)
            },
            files=files
        )

        # if 'error' in api_response:
        #     raise Exception("Transloadit Assembly API call error  - assembly {0} - asset {1}".format(
        #         api_response['assembly_id'], self.pk))
        # elif 'ok' in api_response:
        #     return True
        # else:
        #     raise Exception("Transloadit Assembly API response unknown  - assembly {0} - asset {1}".format(
        #         api_response['assembly_id'], self.pk))

        return response.json()


transloadit = TransloaditClient(settings.TRANSLOADIT_AUTH_KEY, settings.TRANSLOADIT_AUTH_SECRET)



FILETYPES = {
    'doc': ('Word', 'Microsoft Word Document'),
    'docx': ('Word', 'Microsoft Word Open XML Document'),
    'log': ('Text', 'Log File'),
    'msg': ('Text', 'Outlook Mail Message'),
    'odt': ('Text', 'OpenDocument Text Document'),
    'pages': ('Text', 'Pages Document'),
    'rtf': ('Text', 'Rich Text Format File'),
    'tex': ('Text', 'LaTeX Source Document'),
    'txt': ('Text', 'Plain Text File'),
    'wpd': ('Text', 'WordPerfect Document'),
    'wps': ('Text', 'Microsoft Works Word Processor Document'),
    'csv': ('Text', 'Comma Separated Values File'),
    'dat': ('Text', 'Data File'),
    'gbr': ('Text', 'Gerber File'),
    'ged': ('Text', 'GEDCOM Genealogy Data File'),
    'ibooks': ('Text', 'Multi-Touch iBook'),
    'key': ('Text', 'Keynote Presentation'),
    'keychain': ('Text', 'Mac OS X Keychain File'),
    'pps': ('Powerpoint', 'PowerPoint Slide Show'),
    'ppt': ('Powerpoint', 'PowerPoint Presentation'),
    'pptx': ('Powerpoint', 'PowerPoint Open XML Presentation'),
    'sdf': ('Text', 'Standard Data File'),
    'tar': ('Archive', 'Consolidated Unix File Archive'),
    'vcf': ('Text', 'vCard File'),
    'xml': ('Text', 'XML File'),
    'aif': ('Audio', 'Audio Interchange File Format'),
    'aiff': ('Audio', 'Audio Interchange File Format'),
    'iff': ('Audio', 'Interchange File Format'),
    'm3u': ('Audio', 'Media Playlist File'),
    'm4a': ('Audio', 'MPEG-4 Audio File'),
    'mid': ('Audio', 'MIDI File'),
    'mp3': ('Audio', 'MP3 Audio File'),
    'mpa': ('Audio', 'MPEG-2 Audio File'),
    'ra': ('Audio', 'Real Audio File'),
    'wav': ('Audio', 'WAVE Audio File'),
    'wma': ('Audio', 'Windows Media Audio File'),
    '3g2': ('Video', '3GPP2 Multimedia File'),
    '3gp': ('Video', '3GPP Multimedia File'),
    'asf': ('Video', 'Advanced Systems Format File'),
    'asx': ('Video', 'Microsoft ASF Redirector File'),
    'avi': ('Video', 'Audio Video Interleave File'),
    'flv': ('Video', 'Flash Video File'),
    'm4v': ('Video', 'iTunes Video File'),
    'mov': ('Video', 'Apple QuickTime Movie'),
    'mp4': ('Video', 'MPEG-4 Video File'),
    'mpg': ('Video', 'MPEG Video File'),
    'rm': ('Video', 'Real Media File'),
    'srt': ('Video', 'SubRip Subtitle File'),
    'swf': ('Video', 'Shockwave Flash Movie'),
    'vob': ('Video', 'DVD Video Object File'),
    'wmv': ('Video', 'Windows Media Video File'),
    'bmp': ('Image', 'Bitmap Image File'),
    'dds': ('Image', 'DirectDraw Surface'),
    'gif': ('Image', 'Graphical Interchange Format File'),
    'jpg': ('Image', 'JPEG Image'),
    'jpeg': ('Image', 'JPEG Image'),
    'png': ('Image', 'Portable Network Graphic'),
    'psd': ('Image', 'Adobe Photoshop Document'),
    'psp': ('Image', 'PaintShop Pro Image'),
    'tga': ('Image', 'Targa Graphic'),
    'thm': ('Image', 'Thumbnail Image File'),
    'tif': ('Image', 'Tagged Image File'),
    'tiff': ('Image', 'Tagged Image File Format'),
    'yuv': ('Image', 'YUV Encoded Image File'),
    'ai': ('Vector', 'Adobe Illustrator File'),
    'eps': ('Vector', 'Encapsulated PostScript File'),
    'ps': ('Vector', 'PostScript File'),
    'svg': ('Vector', 'Scalable Vector Graphics File'),
    'indd': ('Page', 'layout Adobe InDesign Document'),
    'pct': ('Page', 'layout Picture File'),
    'pdf': ('PDF', 'Portable Document Format File'),
    'xlr': ('Excel', 'Works Spreadsheet'),
    'xls': ('Excel', 'Excel Spreadsheet'),
    'xlsx': ('Excel', 'Microsoft Excel Open XML Spreadsheet'),
    'asp': ('Web', 'Active Server Page'),
    'aspx': ('Web', 'Active Server Page Extended File'),
    'cer': ('Web', 'Internet Security Certificate'),
    'cfm': ('Web', 'ColdFusion Markup File'),
    'csr': ('Web', 'Certificate Signing Request File'),
    'css': ('Web', 'Cascading Style Sheet'),
    'htm': ('Web', 'Hypertext Markup Language File'),
    'html': ('Web', 'Hypertext Markup Language File'),
    'js': ('Web', 'JavaScript File'),
    'jsp': ('Web', 'Java Server Page'),
    'php': ('Web', 'PHP Source Code File'),
    'rss': ('Web', 'Rich Site Summary'),
    'xhtml': ('Web', 'Extensible Hypertext Markup Language File'),
    'fnt': ('Font', 'Windows Font File'),
    'fon': ('Font', 'Generic Font File'),
    'font': ('Font', 'Generic Font File'),
    'otf': ('Font', 'OpenType Font'),
    'ttf': ('Font', 'TrueType Font'),
    '7z': ('Archive', '7-Zip Compressed File'),
    'cbr': ('Archive', 'Comic Book RAR Archive'),
    'deb': ('Archive', 'Debian Software Package'),
    'gz': ('Archive', 'Gnu Zipped Archive'),
    'pkg': ('Archive', 'Mac OS X Installer Package'),
    'rar': ('Archive', 'WinRAR Compressed Archive'),
    'rpm': ('Archive', 'Red Hat Package Manager File'),
    'sitx': ('Archive', 'StuffIt X Archive'),
    'tar': ('Archive', 'Tarball File'),
    'tar.gz': ('Archive', 'Compressed Tarball File'),
    'tar.bz2': ('Archive', 'Compressed Tarball File'),
    'zip': ('Archive', 'Zipped File'),
    'zipx': ('Archive', 'Extended Zip File')
}


def get_filetype(extension):
    try:
        return FILETYPES['{0}'.format(extension)]
    except:
        return ('Unknown', 'Unknown')


def splitext(path):
    if not path:
        return '', '', False
    for ext in FILETYPES.keys():
        if path.lower().endswith('.{0}'.format(ext)):
            basename, ext = path[:-len(ext) - 1], path[-len(ext):]
            secureext = True
            break
    else:
        basename, ext = os.path.splitext(path)
        if basename.endswith('.'):
            basename = basename.split('.')[0]
        if ext.startswith('.'):
            ext = ext.split('.')[1]
        secureext = False

    return basename, ext.lower(), secureext

    # for ext in ['.tar.gz', '.tar.bz2']:
    #     if path.endswith(ext):
    #         path, ext = path[:-len(ext)], path[-len(ext):]
    #         break
    # else:
    #     path, ext = os.path.splitext(path)


def get_uploaded_file_attributes(file_name):
    title, extension, _ = splitext(file_name)
    return {
        "title": title,
        "extension": extension,
        "filetype": get_filetype(extension)[0]
    }


def start_transloadit_conversion(asset):
    """
    File conversion using transloadit.com services
    Use it to generate thumbnails for asset

    "cover" steps are for previewing the media ( in lists, linkedAssets).
    "working" steps are for working on the media ( in item content ).

    :return: Transloadit response as json
    """
    # In Transloadit domain assemblies are a set of commands (pipeline processes or 'steps') for manipulating files.
    # Depending on the file mime in input Translaodit figures out which step to use (image, video or audio)
    s3_bucket = settings.AWS_STORAGE_BUCKET_NAME
    s3_key = settings.AWS_ACCESS_KEY_ID
    s3_secret = settings.AWS_SECRET_ACCESS_KEY
    s3_bucket_region = settings.AWS_REGION
    ffmpeg_stack = 'v3.3.3'
    imagemagick_stack = 'v2.0.7'

    assembly_dict = {
        'notify_url': get_fully_qualified_url(reverse('api-assets-notify-transloadit', kwargs={'pk': asset.pk, })),
        'steps': {
            # Import the original doc
            'original': {
                'robot': '/s3/import',
                'bucket': s3_bucket,
                'bucket_region': s3_bucket_region,
                'key': s3_key,
                'secret': s3_secret,
                'path': asset.originalpath,
                'result': 'true',
            },

            # Check for viruses and stop if found
            'originalnovirus': {
                'robot': '/file/virusscan',
                'use': 'original',
                'result': True,
                'error_on_decline': True
            },

            # Create a filter for audio files
            'onlyAudioFile': {
                'robot': '/file/filter',
                'use': 'originalnovirus',
                'declines': [['${file.meta.audio_bitrate}', '=', '']],
                'error_on_decline': False,
                'result': True,
            },

            ##########################################
            # Images
            ##########################################

            ## If image first we optimize to reduce size without quality loss
            'imageoptimized': {
                'robot': '/image/optimize',
                'use': 'originalnovirus',
                'progressive': True,
                'imagemagick_stack': imagemagick_stack,
                'result': True,
                'format': 'jpg',
            },

            ## From an optimized image file we create a cover preview for list view
            'coverImage': {
                'robot': '/image/resize',
                'use': 'imageoptimized',
                'imagemagick_stack': imagemagick_stack,
                'result': True,
                'width': 100,
                'format': 'jpg',
            },

            ##########################################
            # Videos
            ##########################################

            ## If video we extract an image thumbnail
            'videoThumb': {
                'robot': '/video/thumbs',
                'use': 'originalnovirus',
                'ffmpeg_stack': ffmpeg_stack,
                'count': 1
            },

            ## Generate thumbnail for list view. For detail view we will use a player.
            'coverVideo': {
                'robot': '/image/resize',
                'use': 'videoThumb',
                'imagemagick_stack': imagemagick_stack,
                'width': 100,
                'format': 'jpg',
            },

            ##########################################
            # Documents
            ##########################################

            # If original file is a PDF we generate a thumbnail of the first page for list views. PDF.js is used for detailed view.
            'coverDocument': {
                'robot': '/document/thumbs',
                'use': 'originalnovirus',
                'resize_strategy': 'fit',
                'page': 1,
                'width': 100,
                'format': 'jpg',
            },


            ##########################################
            # Working documents
            ##########################################

            # Create the working version, depending on the file type
            'workingImage': {
                'robot': '/image/resize',
                'use': 'imageoptimized',
                'imagemagick_stack': imagemagick_stack,
                'width': 1000,
                'format': 'jpg',
            },
            'workingDocument': {
                'robot': '/document/thumbs',
                'use': 'originalnovirus',
                'resize_strategy': 'fit',
                'width': 1000,
                'format': 'jpg',
            },
            'workingVideo': {
                'robot': '/video/encode',
                'use': 'originalnovirus',
                'ffmpeg_stack': ffmpeg_stack,
                'preset': 'hls-360p',
                'resize_strategy': 'fit',
                'width': 640,
                'height': 360,
            },
            'workingAudio': {
                'robot': '/audio/encode',
                'use': 'onlyAudioFile',
                'ffmpeg_stack': ffmpeg_stack,
                'preset': 'mp3',
            },

            # Upload cover to S3
            'uploadCoverToS3': {
                'use': ['coverImage', 'coverVideo', 'coverDocument'],
                'robot': '/s3/store',
                'bucket': s3_bucket,
                'key': s3_key,
                'secret': s3_secret,
                'bucket_region': s3_bucket_region,
                'acl': 'public-read',
                'headers': {
                    'Content-Type': '${file.mime}',
                    'Content-Disposition': 'attachment',
                    'Cache-Control': 'max-age=0',
                },
                'path': asset.coverpath
            },

            # Upload working image to S3
            'uploadWorkingToS3': {
                'use': ['workingImage', 'workingVideo', 'workingAudio'],
                'robot': '/s3/store',
                'bucket': s3_bucket,
                'key': s3_key,
                'secret': s3_secret,
                'bucket_region': s3_bucket_region,
                'acl': 'public-read',
                'headers': {
                    'Content-Type': '${file.mime}',
                    'Content-Disposition': 'attachment',
                    'Cache-Control': 'max-age=0',
                },
                'path': asset.image_working_path
            },
            # Upload working document to S3
            'uploadWorkingDocumentToS3': {
                'use': ['workingDocument'],
                'robot': '/s3/store',
                'bucket': s3_bucket,
                'key': s3_key,
                'secret': s3_secret,
                'bucket_region': s3_bucket_region,
                'acl': 'public-read',
                'headers': {
                    'Content-Type': '${file.mime}',
                    'Content-Disposition': 'attachment',
                    'Cache-Control': 'max-age=0',
                },
                'path': asset.document_working_path_transloadit
            },
        }
    }

    request = transloadit.request(**assembly_dict)

    # In dev, setup a timer to check the transloadit status after 5 seconds,
    # to simulate a call to notify_transloadit
    if settings.DEBUG:
        Timer(5.0, simulate_notify_transloadit, args=(asset.id,) ).start()

    return request


def simulate_notify_transloadit(asset_id):
    """
    Simulate a call to notify_transloadit for dev environment
    """
    asset = Asset.objects.get(id=asset_id)
    if asset.assembly_url:
        conversion_data = requests.get(asset.assembly_url).json()
        asset.update_conversion_data(conversion_data)
        asset.save()
        broadcaster.broadcast_asset_conversion_status(asset)


def create_asset(request, serializer, asset_data):
    """ Asset creation finalization process, shared between :
      - standard create/perform_create on AssetViewSet
      - create on ProjectViewSet
      - create/update Project/Item Public Form
    """
    created_by = request.user if request.user.is_authenticated else None
    asset = serializer.save(
        desk=request.desk,
        created_by=created_by,
        file=asset_data['file'],
        **get_uploaded_file_attributes(asset_data.get('fileName'))
    )

    conversion_data = start_transloadit_conversion(asset)
    asset.update_conversion_data(conversion_data)
    asset.save()

    return asset


def link_uploaded_assets(request, target, assets_data):
    """
    For model instance creation through API,
    the frontend will send an array of asset data corresponding to the uploaded files.
    Here we create the corresponding Asset instances, and link them to the newly created instance (target)
    """
    for asset_data in assets_data:
        # Temporary creation by assetId
        asset = Asset.objects.get(id=asset_data['assetId'])
        asset_serializer = AssetSerializer(asset, data=asset_data)
        asset_serializer.is_valid(raise_exception=True)
        asset = create_asset(request, asset_serializer, asset_data)

        # When creation by UUID will be back
        # asset = Asset.objects.create(
        #     desk=self.request.desk,
        #     file=asset['file'],
        #     **get_uploaded_file_attributes(asset['fileName'])
        # )

        target.assets.add(asset)


def start_transloadit_assets_zip(assets):
    """
    File archiving in a zip, using transloadit.com services

    :return: Transloadit response as json
    """
    # Declare all import steps
    steps = {
        'asset-{}'.format(asset.pk):
        {
            'robot': '/http/import',
            'url': asset.file_url,
            'force_name': asset.get_name(normalized=True)
        }
        for asset in assets
    }
    # Add the zip step
    steps['concat'] = {
        'use': {
            'steps': ['asset-{}'.format(asset.pk) for asset in assets],
            'bundle_steps': True
        },
        'robot': '/file/compress',
        'format': 'zip',
        'file_layout': 'simple'
    }

    return transloadit.request(steps=steps)
