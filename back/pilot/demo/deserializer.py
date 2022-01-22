import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import Deserializer as JsonDeserializer
from django.db import models

from pilot.desks.models import Desk
from pilot.organizations.models import Organization
from pilot.pilot_users.models import PilotUser
from pilot.demo.config import get_dump_path_for_model, DEMO_MODELS, ORGANIZATION_DUMP_PATH, \
    DESK_DUMP_PATH, USERS_DUMP_PATH, ANCHOR_DATE, SUBSCRIPTION_PLAN_DUMP_PATH, TEAMS_DUMP_PATH
from pilot.utils.search import FullTextSearchModel, UnaccentFunc


def wipe_all_data():
    for model_config in DEMO_MODELS:
        model_config.model.objects.all().delete()

    Desk.objects.all().delete()
    Organization.objects.all().delete()
    ContentType.objects.all().delete()


def deserialize_instances(dump_path):
    with open(dump_path, 'r') as dump_file:
        serialized_data = dump_file.read()

    deserializer = JsonDeserializer(serialized_data)

    date_fields = None

    for deserialized in deserializer:
        instance = deserialized.object

        # On first instance, init the date fields
        if date_fields is None:
            date_fields = [
                field.name for field in instance._meta.get_fields()
                if isinstance(field, (models.DateField, models.DateTimeField))
            ]

        date_delta = ANCHOR_DATE - datetime.date.today()
        for field_name in date_fields:
            date_before = getattr(instance, field_name)
            if date_before:
                setattr(instance, field_name, date_before + date_delta)

        if isinstance(instance, FullTextSearchModel):
            instance.search_vector = instance.get_search_vector()
            search_document = instance.get_search_document()
            # With big search content, there's a weird error with postgres that appears only when loading demo data.
            # The db complains that the GIN index is too big.
            # Surprinsingly, this error does not show up when saving the items with the web server.
            # This will only impact the partial search on  the demo site, which is sad but not too critical.
            if len(search_document) > 2000:
                search_document = search_document[0:2000]
            instance.partial_search_document = UnaccentFunc(search_document)

        deserialized.save()


def load_demo_desk():
    if not settings.ON_DEMO_SITE:
        raise Exception("Demo desk can only be loaded on the demo site")

    # Begin by wiping out all the existing data
    wipe_all_data()

    # We'll always need a user 1 for all kind of auto-generated objects
    PilotUser.objects.create(id=1)

    deserialize_instances(SUBSCRIPTION_PLAN_DUMP_PATH)
    deserialize_instances(TEAMS_DUMP_PATH)
    deserialize_instances(USERS_DUMP_PATH)
    deserialize_instances(ORGANIZATION_DUMP_PATH)
    deserialize_instances(DESK_DUMP_PATH)

    for model_config in DEMO_MODELS:
        deserialize_instances(get_dump_path_for_model(model_config.model))
