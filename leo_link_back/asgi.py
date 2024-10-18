"""
ASGI config for leo_link_back project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leo_link_back.settings')

# Aplicación ASGI de Django
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from api.routing import websocket_urlpatterns

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        try:
            query_string = scope.get('query_string', b'').decode()
            query_params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
            token = query_params.get('token', '')
            access_token = AccessToken(token)
            User = get_user_model()
            user = await User.objects.aget(id=access_token['user_id'])
            scope['user'] = user
        except Exception:
            scope['user'] = AnonymousUser()
        return await super().__call__(scope, receive, send)

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            TokenAuthMiddleware(
                URLRouter(websocket_urlpatterns)
            )
        )
    ),
})
# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leo_link_back.settings')

# application = get_asgi_application()
