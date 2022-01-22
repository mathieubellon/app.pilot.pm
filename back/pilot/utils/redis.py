import json
import logging
import urllib.parse as urlparse

from django.conf import settings
from redis import Redis

logger = logging.getLogger(__name__)

urlparse.uses_netloc.append('redis')
redis_url = urlparse.urlparse(settings.REDIS_URL)
redis_client = Redis(
    host=redis_url.hostname,
    port=redis_url.port,
    password=redis_url.password
)

# Check that the server is running, and send an alert otherwise
try:
    redis_client.ping()
except:
    logger.error("Redis server is not accessible", exc_info=True)


redis_pubsub = redis_client.pubsub(ignore_subscribe_messages=True)


class PUBSUB_CHANNELS:
    ITEM_CONTENT_UPDATED = 'item_content_updated'


def pubsub_publish(channel, data):
    redis_client.publish(channel, json.dumps(data))


def pubsub_subscribe(channel, handler):
    def __handler__(message):
        handler(json.loads(message['data']))
    redis_pubsub.subscribe(**{channel: __handler__})