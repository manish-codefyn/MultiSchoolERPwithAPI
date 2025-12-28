from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.api.serializers import TenantAwareSerializer, RelatedFieldAlternative
from apps.analytics.models import (
    AuditAnalysisReport, AuditPattern, AuditAlert, AuditDashboard,
    AuditMetric, AuditMetricValue, DataSource, KPIModel
)
# Import core if needed for AuditLog, but usually string reference or ID is fine for M2M unless detailed view needed.
# from apps.core.models import AuditLog

User = get_user_model()

# ============================================================================
# HELPER SERIALIZERS
# ============================================================================

class SimpleUserSerializer(serializers.ModelSerializer):
    """Simple serializer for user details"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role']

# ============================================================================
# AUDIT SERIALIZERS
# ============================================================================

class AuditAnalysisReportSerializer(TenantAwareSerializer):
    generated_by_detail = RelatedFieldAlternative(
        source='generated_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = AuditAnalysisReport
        fields = '__all__'

class AuditPatternSerializer(TenantAwareSerializer):
    class Meta:
        model = AuditPattern
        fields = '__all__'

class AuditAlertSerializer(TenantAwareSerializer):
    pattern_detail = RelatedFieldAlternative(
        source='pattern',
        read_only=True,
        serializer=AuditPatternSerializer
    )
    assigned_to_detail = RelatedFieldAlternative(
        source='assigned_to',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    acknowledged_by_detail = RelatedFieldAlternative(
        source='acknowledged_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    resolved_by_detail = RelatedFieldAlternative(
        source='resolved_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = AuditAlert
        fields = '__all__'

class AuditDashboardSerializer(TenantAwareSerializer):
    owner_detail = RelatedFieldAlternative(
        source='owner',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = AuditDashboard
        fields = '__all__'

class AuditMetricSerializer(TenantAwareSerializer):
    class Meta:
        model = AuditMetric
        fields = '__all__'

class AuditMetricValueSerializer(TenantAwareSerializer):
    metric_detail = RelatedFieldAlternative(
        source='metric',
        read_only=True,
        serializer=AuditMetricSerializer
    )

    class Meta:
        model = AuditMetricValue
        fields = '__all__'

# ============================================================================
# ANALYTICS SERIALIZERS
# ============================================================================

class DataSourceSerializer(TenantAwareSerializer):
    class Meta:
        model = DataSource
        fields = '__all__'

class KPIModelSerializer(TenantAwareSerializer):
    created_by_detail = RelatedFieldAlternative(
        source='created_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    
    # Computed
    current_value = serializers.FloatField(read_only=True)
    trend = serializers.CharField(read_only=True)

    class Meta:
        model = KPIModel
        fields = '__all__'
        read_only_fields = ['id', 'current_value', 'trend']
