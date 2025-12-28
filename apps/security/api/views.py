from rest_framework import viewsets
from apps.core.api.permissions import TenantAccessPermission, RoleRequiredPermission
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions.mixins import TenantAccessMixin
from apps.security.models import *
from .serializers import *

class SecurityPolicyViewSet(viewsets.ModelViewSet):
    queryset = SecurityPolicy.objects.all()
    serializer_class = SecurityPolicySerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class PasswordPolicyViewSet(viewsets.ModelViewSet):
    queryset = PasswordPolicy.objects.all()
    serializer_class = PasswordPolicySerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class SessionPolicyViewSet(viewsets.ModelViewSet):
    queryset = SessionPolicy.objects.all()
    serializer_class = SessionPolicySerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class AccessControlPolicyViewSet(viewsets.ModelViewSet):
    queryset = AccessControlPolicy.objects.all()
    serializer_class = AccessControlPolicySerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class SecurityIncidentViewSet(viewsets.ModelViewSet):
    queryset = SecurityIncident.objects.all()
    serializer_class = SecurityIncidentSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class IncidentTimelineViewSet(viewsets.ModelViewSet):
    queryset = IncidentTimeline.objects.all()
    serializer_class = IncidentTimelineSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class ThreatIntelligenceViewSet(viewsets.ModelViewSet):
    queryset = ThreatIntelligence.objects.all()
    serializer_class = ThreatIntelligenceSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class SecurityScanViewSet(viewsets.ModelViewSet):
    queryset = SecurityScan.objects.all()
    serializer_class = SecurityScanSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

