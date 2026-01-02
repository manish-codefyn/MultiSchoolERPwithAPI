from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from apps.core import views as core_views


schema_view = get_schema_view(
   openapi.Info(
      title="EduERP API",
      default_version='v1',
      description="API documentation",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@schoolerp.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # API URLs (Priority)
    path("", include("eduerp.api_urls")),
    
    # Swagger / Redoc
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),


    path("admin/", admin.site.urls),

    # Web / App URLs
    path("accounts/", include("apps.auth.urls")),
    path("core/", include("apps.core.urls", namespace="core")),
    path("academics/", include("apps.academics.urls")),
    path("analytics/", include("apps.analytics.urls", namespace="analytics")),
    path("attendance/", include("apps.attendance.urls", namespace="attendance")),
    path("assignments/", include("apps.assignments.urls", namespace="assignments")),
    path("certificates/", include("apps.certificates.urls", namespace="certificates")),
    path("communications/", include("apps.communications.urls")),
    path("admission/", include("apps.admission.urls", namespace="admission")),
    path("exams/", include("apps.exams.urls", namespace="exams")),
    path("events/", include("apps.events.urls", namespace="events")),
    path("library/", include("apps.library.urls", namespace="library")),
    path("finance/", include("apps.finance.urls", namespace="finance")),
    path("hostel/", include("apps.hostel.urls", namespace="hostel")),
    path("hr/", include("apps.hr.urls", namespace="hr")),
    path("inventory/", include("apps.inventory.urls", namespace="inventory")),
    path("security/", include("apps.security.urls", namespace="security")),
    path("students/", include("apps.students.urls", namespace="students")),
    path("portal/", include("apps.student_portal.urls", namespace="student_portal")),
    path("transportation/", include("apps.transportation.urls", namespace="transportation")),
    path("users/", include("apps.users.urls", namespace="users")),


    # Tenants + Public
    path("", include("apps.tenants.urls", namespace="tenants")),
    path("", include("apps.public.urls")),
    # Master Dashboard
    path("dashboard/",core_views.MasterDashboardView.as_view(),name="master_dashboard",),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


handler404 = "apps.core.views.custom_page_not_found_view"
handler500 = "apps.core.views.custom_error_view"
handler403 = "apps.core.views.custom_permission_denied_view"
handler400 = "apps.core.views.custom_bad_request_view"
