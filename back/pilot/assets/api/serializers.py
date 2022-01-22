from rest_framework import serializers
from django.template.defaultfilters import filesizeformat, lower

from pilot.assets.models import Asset, AssetRight
from pilot.channels.api.light_serializers import ChannelLightSerializer
from pilot.items.api.light_serializers import ItemLightSerializer
from pilot.labels.api.serializers import LabelLightSerializer
from pilot.notifications.api.serializers import ReminderSerializer
from pilot.pilot_users.api.serializers import PilotUserLightSerializer
from pilot.projects.api.light_serializers import ProjectLightSerializer
from pilot.utils.api.serializers import SmartPrimaryKeyRelatedField


class AssetRightSerializer(serializers.ModelSerializer):
    asset_id = SmartPrimaryKeyRelatedField(required=True, allow_null=False)
    medium = LabelLightSerializer(read_only=True)
    medium_id = SmartPrimaryKeyRelatedField(required=True, allow_null=False)
    reminders = ReminderSerializer(many=True, read_only=True)

    class Meta:
        model = AssetRight
        fields = (
            'asset_id',
            'expiry',
            'id',
            'medium',
            'medium_id',
            'reminders',
        )


class AssetLightSerializer(serializers.ModelSerializer):
    """
    Used for :
    - AssetList
    - LinkedAssets
    - AssetWidget (in ItemContentFormField )
    """
    filetype = serializers.SerializerMethodField()
    folder = LabelLightSerializer(read_only=True)
    name = serializers.ReadOnlyField()
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Asset
        fields = (
            'cover_url',
            'created_at',
            'extension',
            'file_url',
            'filetype',
            'folder',
            'folder_id',
            'html_alt',
            'html_caption',
            'html_title',
            'id',
            'in_media_library',
            'is_assembly_completed',
            'is_assembly_error',
            'is_assembly_executing',
            'is_file_asset',
            'is_image',
            'name',
            'title',
            'url',
            'version',
            'working_urls',
            'width',
        )

    def get_filetype(self, asset):
        return lower(asset.filetype)


class AssetSerializer(serializers.ModelSerializer):
    asset_rights = AssetRightSerializer(many=True, required=False, read_only=True)
    channels = ChannelLightSerializer(many=True, read_only=True)
    created_by = PilotUserLightSerializer(read_only=True)
    filetype = serializers.SerializerMethodField()
    folder = LabelLightSerializer(read_only=True)
    folder_id = SmartPrimaryKeyRelatedField(required=False, allow_null=True)
    items = ItemLightSerializer(many=True, read_only=True)
    projects = ProjectLightSerializer(many=True, read_only=True)
    readable_file_size = serializers.SerializerMethodField(read_only=True)
    # The title is sometime set by the API, from the filename. Set it as not required.
    title = serializers.CharField(required=False)
    updated_by = PilotUserLightSerializer(read_only=True)
    url = serializers.ReadOnlyField(source='get_absolute_url')

    class Meta:
        model = Asset
        fields = (
            'asset_rights',
            'channels',
            'conversions',
            'cover_url',
            'created_at',
            'created_by',
            'description',
            'extension',
            'file_url',
            'filetype',
            'folder',
            'folder_id',
            'height',
            'html_alt',
            'html_caption',
            'html_title',
            'id',
            'in_media_library',
            'is_assembly_completed',
            'is_assembly_error',
            'is_assembly_executing',
            'is_file_asset',
            'is_image',
            'items',
            'mime',
            'name',
            'projects',
            'readable_file_size',
            'size',
            'title',
            'updated_at',
            'updated_by',
            'url',
            'uuid',
            'version',
            'width',
            'working_urls',
        )
        read_only_fields = (
            'conversions',
            'cover_url',
            'created_at',
            'extension',
            'file_url',
            'is_assembly_completed',
            'is_assembly_error',
            'is_assembly_executing',
            'is_file_asset',
            'is_image',
            'items',
            'name',
            'updated_at',
            'version'
        )

    def get_readable_file_size(self, asset):
        return filesizeformat(asset.size)

    def get_filetype(self, asset):
        return lower(asset.filetype)


class UrlAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = (
            'description',
            'in_media_library',
            'title',
            'url',
        )


class AssetForSharingSerializer(serializers.ModelSerializer):
    filetype = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = (
            'cover_url',
            'extension',
            'file_url',
            'filetype',
            'id',
            'is_assembly_executing',
            'name',
            'title',
        )
        read_only_fields = (
            'cover_url',
            'extension',
            'file_url',
            'is_assembly_executing',
            'id',
            'items',
            'name',
            'title',
        )

    def get_filetype(self, asset):
        return lower(asset.filetype)
