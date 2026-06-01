from django.urls import re_path
from .consumers import OrderConsumer, NotificationConsumer, UpdateConsumer

websocket_urlpatterns = [
    re_path(r'ws/orders/$', OrderConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/customer/$',UpdateConsumer.as_asgi()),
]
