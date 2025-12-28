from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.core.api.permissions import TenantAccessPermission, RoleRequiredPermission
from rest_framework.permissions import IsAuthenticated
from apps.core.permissions.mixins import TenantAccessMixin
from apps.tenants.models import *
from .serializers import *

class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

    @action(detail=False, methods=['get'])
    def current(self, request):
        if not hasattr(request.user, 'tenant'):
             return Response({"detail": "User has no tenant assigned."}, status=400)
        
        serializer = self.get_serializer(request.user.tenant)
        return Response(serializer.data)

class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class TenantConfigurationViewSet(viewsets.ModelViewSet):
    queryset = TenantConfiguration.objects.all()
    serializer_class = TenantConfigurationSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class PaymentConfigurationViewSet(viewsets.ModelViewSet):
    queryset = PaymentConfiguration.objects.all()
    serializer_class = PaymentConfigurationSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class AnalyticsConfigurationViewSet(viewsets.ModelViewSet):
    queryset = AnalyticsConfiguration.objects.all()
    serializer_class = AnalyticsConfigurationSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class SystemNotificationViewSet(viewsets.ModelViewSet):
    queryset = SystemNotification.objects.all()
    serializer_class = SystemNotificationSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class APIServiceCategoryViewSet(viewsets.ModelViewSet):
    queryset = APIServiceCategory.objects.all()
    serializer_class = APIServiceCategorySerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class APIServiceViewSet(viewsets.ModelViewSet):
    queryset = APIService.objects.all()
    serializer_class = APIServiceSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class TenantAPIKeyViewSet(viewsets.ModelViewSet):
    queryset = TenantAPIKey.objects.all()
    serializer_class = TenantAPIKeySerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class APIUsageLogViewSet(viewsets.ModelViewSet):
    queryset = APIUsageLog.objects.all()
    serializer_class = APIUsageLogSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class TenantSecretViewSet(viewsets.ModelViewSet):
    queryset = TenantSecret.objects.all()
    serializer_class = TenantSecretSerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class VideoAPIKeyViewSet(viewsets.ModelViewSet):
    queryset = VideoAPIKey.objects.all()
    serializer_class = VideoAPIKeySerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class WhatsAppAPIKeyViewSet(viewsets.ModelViewSet):
    queryset = WhatsAppAPIKey.objects.all()
    serializer_class = WhatsAppAPIKeySerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class SMSAPIKeyViewSet(viewsets.ModelViewSet):
    queryset = SMSAPIKey.objects.all()
    serializer_class = SMSAPIKeySerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

class AIAPIKeyViewSet(viewsets.ModelViewSet):
    queryset = AIAPIKey.objects.all()
    serializer_class = AIAPIKeySerializer
    permission_classes = [IsAuthenticated, TenantAccessPermission, RoleRequiredPermission]
    required_roles = ['admin', 'super_admin']

