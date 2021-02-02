from django.urls import re_path
from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/ws_support_multi_box/(?P<channel_uuid>[a-zA-Z0-9-]+)/(?P<channel_mux>\w+)$', consumers.SupportMultiBoxConsumer),
]
