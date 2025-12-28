from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.api.serializers import TenantAwareSerializer, RelatedFieldAlternative
from apps.admission.models import (
    AdmissionCycle, AdmissionProgram, OnlineApplication, ApplicationDocument
)
from apps.academics.models import AcademicYear

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

class SimpleAcademicYearSerializer(serializers.ModelSerializer):
    """Simple serializer for academic year"""
    class Meta:
        model = AcademicYear
        fields = ['id', 'name', 'is_current']

# ============================================================================
# ADMISSION CYCLE & PROGRAM SERIALIZERS
# ============================================================================

class AdmissionCycleSerializer(TenantAwareSerializer):
    academic_year_detail = RelatedFieldAlternative(
        source='academic_year',
        read_only=True,
        serializer=SimpleAcademicYearSerializer
    )
    
    # Computed
    is_open = serializers.BooleanField(read_only=True)
    application_count = serializers.IntegerField(read_only=True)
    can_accept_applications = serializers.BooleanField(read_only=True)
    remaining_days = serializers.IntegerField(source='get_remaining_days', read_only=True)

    class Meta:
        model = AdmissionCycle
        fields = '__all__'
        read_only_fields = ['id', 'is_open', 'application_count', 'can_accept_applications', 'remaining_days']

class AdmissionProgramSerializer(TenantAwareSerializer):
    admission_cycle_detail = RelatedFieldAlternative(
        source='admission_cycle',
        read_only=True,
        serializer=AdmissionCycleSerializer
    )
    
    # Computed
    filled_seats = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)
    application_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = AdmissionProgram
        fields = '__all__'
        read_only_fields = ['id', 'filled_seats', 'available_seats', 'application_count']

# ============================================================================
# ONLINE APPLICATION SERIALIZERS
# ============================================================================

class OnlineApplicationSerializer(TenantAwareSerializer):
    admission_cycle_detail = RelatedFieldAlternative(
        source='admission_cycle',
        read_only=True,
        serializer=AdmissionCycleSerializer
    )
    program_detail = RelatedFieldAlternative(
        source='program',
        read_only=True,
        serializer=AdmissionProgramSerializer
    )
    
    # Computed
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    is_eligible = serializers.BooleanField(read_only=True)
    formatted_address = serializers.CharField(read_only=True)

    class Meta:
        model = OnlineApplication
        fields = '__all__'
        read_only_fields = [
            'id', 'application_number', 'submission_date', 'review_date', 'decision_date',
            'full_name', 'age', 'is_eligible', 'formatted_address'
        ]

class ApplicationDocumentSerializer(TenantAwareSerializer):
    application_detail = RelatedFieldAlternative(
        source='application',
        read_only=True,
        serializer=OnlineApplicationSerializer
    )
    verified_by_detail = RelatedFieldAlternative(
        source='verified_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    class Meta:
        model = ApplicationDocument
        fields = '__all__'
        read_only_fields = ['id', 'verified_at']
