from django.urls import path
from .consumers import * 


ws_urlpatterns = [
    path('ws/live_socket/',LiveConsumer.as_asgi()),
]