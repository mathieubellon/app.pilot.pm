from django.db import transaction, IntegrityError
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from pilot.labels.api.filters import LabelFilter
from pilot.labels.api.serializers import LabelSerializer
from pilot.labels.models import Label
from pilot.utils import api as api_utils


class LabelViewSet(api_utils.ActivityModelMixin,
                   api_utils.BulkActionMixin,
                   viewsets.ModelViewSet):
    serializer_class = LabelSerializer
    filter_class = LabelFilter
    permission_classes = [
        api_utils.DeskPermission
    ]

    def get_queryset(self):
        return Label.objects.filter(desk=self.request.desk)

    # ===================
    # Create / Update
    # ===================

    def perform_create(self, serializer):
        return serializer.save(
            desk=self.request.desk,
            created_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    # ===================
    # Custom routes
    # ===================

    @action(detail=False, methods=['POST'])
    def set_order(self, request, *args, **kwargs):
        ids = []
        with transaction.atomic():
            queryset = self.get_queryset()
            for label_order in request.data:
                ids.append(label_order['id'])
                queryset.filter(id=label_order['id']).update(order=label_order['order'])

        queryset = queryset.filter(id__in=ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def merge(self, request, *args, **kwargs):
        """
        Merge multiple labels into a single one :
        1/ Create a new label
        2/ Reassign all instances related to the old labels to the new one
        3/ Delete the old labels
        """
        ids_to_merge = request.data.get('ids_to_merge', [])
        destination = request.data.get('destination', {})

        with transaction.atomic():
            # 1/ Create a new label
            new_label_serializer = LabelSerializer(data=destination)
            new_label_serializer.is_valid(raise_exception=True)
            new_label = self.perform_create(new_label_serializer)

            #2/ Reassign all instances related to the old labels to the new one

            # Get all the fields related to the Label model
            related_fields = Label._meta._get_fields(forward=False, include_parents=False)

            for field in related_fields:
                # For M2M, we use the though table, and the related field will always be named "label"
                if field.many_to_many:
                    related_model = field.through
                    remote_field_name = 'label'
                # For ForeignKey, we use the related model and the remote field name
                else:
                    related_model = field.related_model
                    remote_field_name = field.remote_field.name

                # Filter all instances that are linked to a label to merge
                filter_kwargs = {remote_field_name + '__in': ids_to_merge}
                # Set the relation to the newly created label
                update_kwargs = {remote_field_name: new_label}
                related_instances = related_model.objects.filter(**filter_kwargs)
                # Execute the update directly in the db
                try:
                    with transaction.atomic():  # Create a savepoint
                        related_instances.update(**update_kwargs)
                except IntegrityError:
                    # With M2M, we may end up with multiple relations to the same label.
                    # Check this case, and wind down to a single relation when needed.
                    if field.many_to_many:
                        for through_instance in related_instances:
                            try:
                                with transaction.atomic():  # Create a savepoint
                                    through_instance.label = new_label
                                    through_instance.save()
                            except IntegrityError:
                                through_instance.delete()  # Multiple through relations, we need to delete this one
                    else:
                        raise

            # 3/ Delete the old labels
            # Filter the queryset on the target type of the created label
            queryset = self.get_queryset().filter(target_type=new_label.target_type)
            queryset.filter(id__in=ids_to_merge).delete()

        # Return the up to date label list
        return Response(self.get_serializer(queryset, many=True).data)

    # ===================
    # Actions
    # ===================

    def get_bulk_action_handlers(self):
        return {
            'delete': self.action_delete,
        }

    def action_delete(self, label, params={}):
        self.destroy_instance(label)
