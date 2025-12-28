from rest_framework import status
from rest_framework.response import Response
from apps.core.api.views import (
    BaseListCreateAPIView, BaseRetrieveUpdateDestroyAPIView
)
from apps.analytics.models import (
    AuditAnalysisReport, AuditPattern, AuditAlert, AuditDashboard,
    AuditMetric, AuditMetricValue, DataSource, KPIModel
)
from apps.analytics.api.serializers import (
    AuditAnalysisReportSerializer, AuditPatternSerializer, AuditAlertSerializer,
    AuditDashboardSerializer, AuditMetricSerializer, AuditMetricValueSerializer,
    DataSourceSerializer, KPIModelSerializer
)

# ============================================================================
# AUDIT VIEWS
# ============================================================================

class AuditAnalysisReportListCreateAPIView(BaseListCreateAPIView):
    model = AuditAnalysisReport
    serializer_class = AuditAnalysisReportSerializer
    search_fields = ['name']
    filterset_fields = ['report_type', 'status', 'generated_by']
    roles_required = ['admin', 'security_officer']

class AuditAnalysisReportDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = AuditAnalysisReport
    serializer_class = AuditAnalysisReportSerializer
    roles_required = ['admin', 'security_officer']


class AuditPatternListCreateAPIView(BaseListCreateAPIView):
    model = AuditPattern
    serializer_class = AuditPatternSerializer
    search_fields = ['name', 'description']
    filterset_fields = ['pattern_type', 'severity', 'is_active']
    roles_required = ['admin', 'security_officer']

class AuditPatternDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = AuditPattern
    serializer_class = AuditPatternSerializer
    roles_required = ['admin', 'security_officer']


class AuditAlertListCreateAPIView(BaseListCreateAPIView):
    model = AuditAlert
    serializer_class = AuditAlertSerializer
    search_fields = ['title', 'description']
    filterset_fields = ['alert_type', 'status', 'severity', 'assigned_to']
    roles_required = ['admin', 'security_officer']

class AuditAlertDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = AuditAlert
    serializer_class = AuditAlertSerializer
    roles_required = ['admin', 'security_officer']


class AuditDashboardListCreateAPIView(BaseListCreateAPIView):
    model = AuditDashboard
    serializer_class = AuditDashboardSerializer
    search_fields = ['name']
    filterset_fields = ['is_default', 'owner']
    roles_required = ['admin', 'security_officer', 'principal']

class AuditDashboardDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = AuditDashboard
    serializer_class = AuditDashboardSerializer
    roles_required = ['admin', 'security_officer', 'principal']


class AuditMetricListCreateAPIView(BaseListCreateAPIView):
    model = AuditMetric
    serializer_class = AuditMetricSerializer
    search_fields = ['name']
    filterset_fields = ['metric_type', 'calculation_schedule']
    roles_required = ['admin', 'security_officer']

class AuditMetricDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = AuditMetric
    serializer_class = AuditMetricSerializer
    roles_required = ['admin', 'security_officer']


class AuditMetricValueListCreateAPIView(BaseListCreateAPIView):
    model = AuditMetricValue
    serializer_class = AuditMetricValueSerializer
    filterset_fields = ['metric', 'period_type']
    roles_required = ['admin', 'security_officer']

class AuditMetricValueDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = AuditMetricValue
    serializer_class = AuditMetricValueSerializer
    roles_required = ['admin', 'security_officer']

# ============================================================================
# ANALYTICS VIEWS
# ============================================================================

class DataSourceListCreateAPIView(BaseListCreateAPIView):
    model = DataSource
    serializer_class = DataSourceSerializer
    search_fields = ['name']
    filterset_fields = ['source_type', 'status', 'sync_frequency']
    roles_required = ['admin', 'it_admin']

class DataSourceDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = DataSource
    serializer_class = DataSourceSerializer
    roles_required = ['admin', 'it_admin']


class KPIModelListCreateAPIView(BaseListCreateAPIView):
    model = KPIModel
    serializer_class = KPIModelSerializer
    search_fields = ['name', 'code']
    filterset_fields = ['category', 'frequency', 'status']
    roles_required = ['admin', 'principal', 'finance_manager']

class KPIModelDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = KPIModel
    serializer_class = KPIModelSerializer
    roles_required = ['admin', 'principal', 'finance_manager']
