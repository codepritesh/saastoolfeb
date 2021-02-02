from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/avg_tool/(?P<channel_uuid>[a-zA-Z0-9-]+)/(?P<channel_mux>\w+)$', consumers.AvgToolConsumer),
]