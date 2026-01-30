"""
ASGI config for abiatechcomm_BE project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from  api_chat.routing  import websocket_urlpatterns
from channels.security.websocket import AllowedHostsOriginValidator
from api_chat.middleware import JWTAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')


django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http':django_asgi_app,
    "websocket":AuthMiddlewareStack(
        JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns)
    ))
})
