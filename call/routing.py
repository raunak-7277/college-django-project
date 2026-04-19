from django.urls import re_path

from .consumers import CallConsumer

websocket_urlpatterns = [
    re_path(r'ws/room/(?P<room_id>[-\w]+)/$', CallConsumer.as_asgi()),
]
