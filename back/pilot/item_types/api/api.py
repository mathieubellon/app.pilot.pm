from django.db import transaction
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from rest_framework import viewsets

from pilot.item_types.api.serializers import ItemTypeSerializer
from pilot.item_types.initial_item_types import get_translated_content_schema, DEFAULT_CONTENT_SCHEMA
from pilot.item_types.item_content_fields import content_schema_to_content_fields
from pilot.item_types.jobs import ItemTypeUpdateJob
from pilot.item_types.models import ItemType
from pilot.utils import api as api_utils


class ItemTypeViewSet(api_utils.ActivityModelMixin,
                      viewsets.ModelViewSet):
    serializer_class = ItemTypeSerializer
    permission_classes = [
        api_utils.DeskPermission,
        api_utils.IsAdminOrReadOnlyPermission
    ]

    def get_queryset(self):
        return ItemType.objects.filter(desk=self.request.desk).annotate(linked_item_count=Count('items'))

    def perform_create(self, serializer):
        serializer.save(
            desk=self.request.desk,
            created_by=self.request.user,
            content_schema=get_translated_content_schema(
                DEFAULT_CONTENT_SCHEMA,
                self.request.user.language
            )
        )

    def perform_update(self, serializer):
        content_fields_before = content_schema_to_content_fields(serializer.instance.content_schema)

        item_type = serializer.save(
            updated_by=self.request.user
        )

        content_fields_after = content_schema_to_content_fields(item_type.content_schema)

        schema_fields_types_before = { field.name: field.type for field in content_fields_before }
        schema_fields_types_after = { field.name: field.type for field in content_fields_after }

        # New fields with a prosemirror editor must be initialized
        new_prosemirror_field_names = [
            field.name for field in content_fields_after
            if field.is_prosemirror and not schema_fields_types_before.get(field.name)
        ]
        # Field schema which has been deleted or had their type changed
        # Must wipe the corresponding data in the items (but not in the item sessions !)
        field_names_to_wipe = [
            field_name for field_name, field_type in schema_fields_types_before.items()
            if schema_fields_types_after.get(field_name) != field_type
        ]
        if field_names_to_wipe or new_prosemirror_field_names:
            ItemTypeUpdateJob.launch_r(self.request, item_type, field_names_to_wipe, new_prosemirror_field_names)

    def perform_destroy(self, item_type):
        """
        We don't actually destroy the instances, but set their "hidden" flag to True
        """
        with transaction.atomic():
            item_type.hide(user=self.request.user)

            item_type.items.all().update(
                updated_by=self.request.user,
                hidden=True
            )

    def get_activity_delete_action_object_str(self, item_type):
        return _("Type de contenu personnalisé: {name}").format(name=item_type.name)





