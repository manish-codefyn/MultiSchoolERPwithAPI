from django.contrib import admin
from django.urls import path, include
from apps.students import views as student_views
from apps.core import views as core_views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="MultiTenant School ERP API",
      default_version='v1',
      description="API documentation for MultiTenant School ERP System",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@schoolerp.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('', student_views.public_home, name='home'),
    # path('students/dashboard/', student_views.StudentDashboardView.as_view(), name='student-dashboard'),
    # Auth URLs
    path("accounts/", include("apps.auth.urls")),
    path("core/", include("apps.core.urls", namespace="core")),  # Added core URLs
    path("academics/", include("apps.academics.urls")),
    path("analytics/", include("apps.analytics.urls", namespace="analytics")),
    path("attendance/", include("apps.attendance.urls", namespace="attendance")),
    path("assignments/", include("apps.assignments.urls", namespace="assignments")),
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
    path("", include("apps.tenants.urls", namespace="tenants")),
    path(
        "transportation/",
        include("apps.transportation.urls", namespace="transportation"),
    ),
    path("users/", include("apps.users.urls", namespace="users")),
    # Master Dashboard
    path(
        "dashboard/", core_views.MasterDashboardView.as_view(), name="master_dashboard"
    ),
    path("", include("apps.public.urls")),
    # path('accounts/login/', core_views.auth_signin, name='login'),
    
    # ============================================
    # API V1
    # ============================================
    path('api/v1/tenants/', include('apps.tenants.api.urls')),
    path('api/v1/users/', include('apps.users.api.urls')),
    path('api/v1/core/', include('apps.core.api.urls')),
    path('api/v1/auth/', include('apps.auth.api.urls')),
    path('api/v1/security/', include('apps.security.api.urls')),
    path('api/v1/academics/', include('apps.academics.api.urls')),
    path('api/v1/admission/', include('apps.admission.api.urls')),
    path('api/v1/analytics/', include('apps.analytics.api.urls')),
    path('api/v1/communications/', include('apps.communications.api.urls')),
    path('api/v1/events/', include('apps.events.api.urls')),
    path('api/v1/exams/', include('apps.exams.api.urls')),
    path('api/v1/finance/', include('apps.finance.api.urls')),
    path('api/v1/hostel/', include('apps.hostel.api.urls')),
    path('api/v1/hr/', include('apps.hr.api.urls')),
    path('api/v1/inventory/', include('apps.inventory.api.urls')),
    path('api/v1/library/', include('apps.library.api.urls')),
    path('api/v1/students/', include('apps.students.api.urls')),
    path('api/v1/transportation/', include('apps.transportation.api.urls')),
    path('api/v1/assignments/', include('apps.assignments.api.urls')),
    
    # ============================================
    # Documentation
    # ============================================
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# ============================================
# ERROR HANDLERS
# ============================================

handler404 = "apps.core.views.custom_page_not_found_view"
handler500 = "apps.core.views.custom_error_view"
handler403 = "apps.core.views.custom_permission_denied_view"
handler400 = "apps.core.views.custom_bad_request_view"
