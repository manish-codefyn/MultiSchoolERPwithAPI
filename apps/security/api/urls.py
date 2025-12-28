from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'securitypolicys', views.SecurityPolicyViewSet)
router.register(r'passwordpolicys', views.PasswordPolicyViewSet)
router.register(r'sessionpolicys', views.SessionPolicyViewSet)
router.register(r'accesscontrolpolicys', views.AccessControlPolicyViewSet)
router.register(r'auditlogs', views.AuditLogViewSet)
router.register(r'securityincidents', views.SecurityIncidentViewSet)
router.register(r'incidenttimelines', views.IncidentTimelineViewSet)
router.register(r'threatintelligences', views.ThreatIntelligenceViewSet)
router.register(r'securityscans', views.SecurityScanViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
