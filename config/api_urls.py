from django.urls import path, include
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# -----------------------------
# API Version Prefix
# -----------------------------
API_PREFIX = f"api/{settings.API_VERSION}/"

# -----------------------------
# Swagger / OpenAPI Schema
# -----------------------------
schema_view = get_schema_view(
    openapi.Info(
        title="MultiTenant School ERP API",
        default_version=settings.API_VERSION,
        description="API documentation",
        contact=openapi.Contact(email="contact@schoolerp.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# -----------------------------
# URL Patterns
# -----------------------------
urlpatterns = [
    path(f"{API_PREFIX}academics/", include("apps.academics.api.urls")),
    path(f"{API_PREFIX}admission/", include("apps.admission.api.urls")),
    path(f"{API_PREFIX}analytics/", include("apps.analytics.api.urls")),
    path(f"{API_PREFIX}assignments/", include("apps.assignments.api.urls")),
    path(f"{API_PREFIX}attendance/", include("apps.attendance.api.urls")),
    path(f"{API_PREFIX}auth/", include("apps.auth.api.urls")),
    path(f"{API_PREFIX}communications/", include("apps.communications.api.urls")),
    path(f"{API_PREFIX}core/", include("apps.core.api.urls")),
    path(f"{API_PREFIX}events/", include("apps.events.api.urls")),
    path(f"{API_PREFIX}exams/", include("apps.exams.api.urls")),
    path(f"{API_PREFIX}finance/", include("apps.finance.api.urls")),
    path(f"{API_PREFIX}hostel/", include("apps.hostel.api.urls")),
    path(f"{API_PREFIX}hr/", include("apps.hr.api.urls")),
    path(f"{API_PREFIX}inventory/", include("apps.inventory.api.urls")),
    path(f"{API_PREFIX}library/", include("apps.library.api.urls")),
    path(f"{API_PREFIX}security/", include("apps.security.api.urls")),
    path(f"{API_PREFIX}students/", include("apps.students.api.urls")),
    path(f"{API_PREFIX}tenants/", include("apps.tenants.api.urls")),
    path(f"{API_PREFIX}public/", include("apps.public.api.urls")),
    path(f"{API_PREFIX}transportation/", include("apps.transportation.api.urls")),
    path(f"{API_PREFIX}users/", include("apps.users.api.urls")),

    # -----------------------------
    # Swagger / Redoc
    # -----------------------------
    path("swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
