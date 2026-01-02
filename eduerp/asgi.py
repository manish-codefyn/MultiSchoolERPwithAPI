
import os
from django.core.asgi import get_asgi_application
from django.core.wsgi import get_wsgi_application
from asgiref.wsgi import WsgiToAsgi

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduerp.settings')

# Use WsgiToAsgi to wrap the sync WSGI app for HTTP requests.
# This prevents SynchronousOnlyOperation errors with django-tenants middleware
# by enforcing a full sync stack for HTTP.
django_http_app = WsgiToAsgi(get_wsgi_application())

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.db import close_old_connections
from django.db import close_old_connections
from urllib.parse import parse_qs
from channels.db import database_sync_to_async

@database_sync_to_async
def set_tenant_schema(tenant):
    from django.db import connection
    connection.set_tenant(tenant)

# Custom Tenant Middleware for ASGI
class TenantASGIContextMiddleware:
    """
    Middleware to resolve tenant from host header and add to scope.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        from django_tenants.utils import get_tenant_model, get_tenant_domain_model, remove_www_and_dev
        from django.db import connection

        if scope['type'] in ['http', 'websocket']:
            headers = dict(scope['headers'])
            host_header = headers.get(b'host', b'').decode('utf-8').split(':')[0]
            
            # Simple tenant resolution
            hostname = remove_www_and_dev(host_header)
            TenantModel = get_tenant_model()
            DomainModel = get_tenant_domain_model()
            
            tenant = None
            try:
                # Lookup the domain first
                domain_obj = await DomainModel.objects.select_related('tenant').aget(domain=hostname)
                tenant = domain_obj.tenant
            except DomainModel.DoesNotExist:
                # Fallback or public
                try:
                    tenant = await TenantModel.objects.aget(schema_name='public')
                except:
                    tenant = None
            
            if tenant:
                # We can't easily set connection.set_tenant() for the whole thread here safely for all cases
                # But for the websocket consumer downstream, passing it in scope is key.
                # For HTTP (handled by django_http_app), valid tenant setup is handled by TenantMainMiddleware
                # inside the WSGI app (which runs in a thread). 
                # So we mostly need this for WebSocket scope.
                scope['tenant'] = tenant
                await set_tenant_schema(tenant)
        
        return await self.inner(scope, receive, send)

# Import routing from apps
from apps.communications.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_http_app,
    "websocket": AllowedHostsOriginValidator(
        TenantASGIContextMiddleware(
            AuthMiddlewareStack(
                URLRouter(
                    websocket_urlpatterns
                )
            )
        )
    ),
})
