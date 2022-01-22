from django.conf.urls import url

from pilot.realtime import consumers

websocket_urlpatterns = [
    url(r'^rt/$', consumers.PilotConsumer),
]