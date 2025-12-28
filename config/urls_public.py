# main urls.py (public schema)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('config.api_urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.auth.urls')),
    path('tenants/', include('apps.tenants.urls', namespace='tenants')),
    path('security/', include('apps.security.urls', namespace='security')),
    path('users/', include('apps.users.urls', namespace='users')),
    path('core/', include('apps.core.urls', namespace='core')),
    path('communications/', include('apps.communications.urls', namespace='communications')),
    path('', include('apps.public.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)