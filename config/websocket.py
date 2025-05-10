from django.urls import re_path
from project.documents.consumers import DocumentConsumer, ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/notifications/document/$', DocumentConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
]
