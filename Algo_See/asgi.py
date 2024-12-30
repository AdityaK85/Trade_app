
import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from Websocket_Utility.routing import ws_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Algo_See.settings')
print('::: ASGI SERVER STARTED :::')
application = get_asgi_application()
application = ProtocolTypeRouter({
	"http": application,
    "websocket": OriginValidator(AuthMiddlewareStack(URLRouter(ws_urlpatterns)), ['*']),
})