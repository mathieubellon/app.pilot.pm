import boto3
from botocore.exceptions import ClientError

from django.conf import settings
from django.core.serializers.json import Serializer as JsonSerializer

from pilot.accounts.models import SubscriptionPlan
from pilot.assets.models import Asset
from pilot.pilot_users.models import PilotUser
from pilot.demo.config import DEMO_MODELS, get_dump_path_for_model, DESK_DUMP_PATH, \
    ORGANIZATION_DUMP_PATH, SUBSCRIPTION_PLAN_DUMP_PATH


class DemoDumpSerializer(JsonSerializer):
    def handle_m2m_field(self, obj, field):
        if isinstance(obj, PilotUser) and field.name == 'teams':
            self._current[field.name] = [team.id for team in obj.teams.filter(desk=self.desk)]
        else:
            super(DemoDumpSerializer, self).handle_m2m_field(obj, field)


def serialize_instances(dump_path, instances, desk=None):
    serializer = DemoDumpSerializer()
    serializer.desk = desk
    serializer.serialize(instances)
    with open(dump_path, 'w') as dump_file:
        dump_file.write(serializer.getvalue())


def serialize_model(model_config, desk):
    model = model_config.model
    dump_path = get_dump_path_for_model(model)

    queryset = model._base_manager.all()
    if model_config.desk_attr:
        queryset = queryset.filter(**{model_config.desk_attr: desk})

    if model == PilotUser:
        queryset = list(queryset)
        for i, user in enumerate(queryset):
            user.email = 'demo{}@demo.com'.format(i+1)

    serialize_instances(dump_path, queryset, desk)


def copy_s3_files(desk):
    PROD_BUCKET_NAME = 'pilotapp-leader'
    DEMO_REGION_NAME = 'eu-west-3'
    DEMO_BUCKET_NAME = 'pilotapp-demo'

    demo_s3 = boto3.resource(
        's3',
        aws_access_key_id=settings.DEMO_COPY_AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.DEMO_COPY_AWS_SECRET_ACCESS_KEY,
        region_name=DEMO_REGION_NAME
    )

    demo_bucket = demo_s3.Bucket(DEMO_BUCKET_NAME)

    # 1 : empty the bucket
    demo_bucket.objects.all().delete()

    # 2 : copy the asset files
    for asset in Asset.objects.filter(desk=desk):
        for key in [
            asset.originalpath,
            asset.coverpath,
            asset.image_working_path,
            asset.document_working_path_transloadit
        ]:
            try:
                demo_bucket.copy(
                    CopySource={'Bucket': PROD_BUCKET_NAME, 'Key': key},
                    Key=key,
                    ExtraArgs=dict(
                        ACL='public-read',
                        MetadataDirective='COPY'
                    )
                )
            except ClientError as e:
                error = e.response.get('Error', {})
                if error.get('Code') == '404':
                    pass
                else:
                    raise


def dump_demo_desk(desk):
    serialize_instances(SUBSCRIPTION_PLAN_DUMP_PATH, SubscriptionPlan.objects.all())
    serialize_instances(ORGANIZATION_DUMP_PATH, [desk.organization])
    serialize_instances(DESK_DUMP_PATH, [desk])

    for model_config in DEMO_MODELS:
        serialize_model(model_config, desk)

    copy_s3_files(desk)
