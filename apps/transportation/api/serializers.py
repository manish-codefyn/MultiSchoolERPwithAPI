from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.api.serializers import TenantAwareSerializer, RelatedFieldAlternative
from apps.transportation.models import (
    Vehicle, Route, RouteStop, TransportAllocation,
    TransportAttendance, MaintenanceRecord, FuelRecord
)

User = get_user_model()

# ============================================================================
# HELPER SERIALIZERS
# ============================================================================

class SimpleUserSerializer(serializers.ModelSerializer):
    """Simple serializer for user details (drivers, attendants)"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role']

# ============================================================================
# FLEET MANAGEMENT SERIALIZERS
# ============================================================================

class VehicleSerializer(TenantAwareSerializer):
    driver_detail = RelatedFieldAlternative(
        source='driver',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    
    # Computed
    is_registration_valid = serializers.BooleanField(read_only=True)
    is_insurance_valid = serializers.BooleanField(read_only=True)
    is_fitness_valid = serializers.BooleanField(read_only=True)
    is_roadworthy = serializers.BooleanField(read_only=True)

    class Meta:
        model = Vehicle
        fields = '__all__'
        read_only_fields = [
            'id', 'is_registration_valid', 'is_insurance_valid', 
            'is_fitness_valid', 'is_roadworthy'
        ]

class RouteSerializer(TenantAwareSerializer):
    vehicle_detail = RelatedFieldAlternative(
        source='vehicle',
        read_only=True,
        serializer=VehicleSerializer
    )
    driver_detail = RelatedFieldAlternative(
        source='driver',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    attendant_detail = RelatedFieldAlternative(
        source='attendant',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    
    # Computed
    student_count = serializers.IntegerField(read_only=True)
    available_seats = serializers.IntegerField(read_only=True)
    can_accommodate_more = serializers.BooleanField(read_only=True)

    class Meta:
        model = Route
        fields = '__all__'
        read_only_fields = ['id', 'student_count', 'available_seats', 'can_accommodate_more']

class RouteStopSerializer(TenantAwareSerializer):
    route_detail = RelatedFieldAlternative(
        source='route',
        read_only=True,
        serializer=RouteSerializer
    )

    class Meta:
        model = RouteStop
        fields = '__all__'

# ============================================================================
# STUDENT TRANSPORT SERIALIZERS
# ============================================================================

class TransportAllocationSerializer(TenantAwareSerializer):
    route_detail = RelatedFieldAlternative(
        source='route',
        read_only=True,
        serializer=RouteSerializer
    )
    pickup_stop_detail = RelatedFieldAlternative(
        source='pickup_stop',
        read_only=True,
        serializer=RouteStopSerializer
    )
    drop_stop_detail = RelatedFieldAlternative(
        source='drop_stop',
        read_only=True,
        serializer=RouteStopSerializer
    )
    
    # Student Info (Flattened)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_admission_number = serializers.CharField(source='student.admission_number', read_only=True)
    
    # Computed
    pickup_time = serializers.TimeField(read_only=True)
    drop_time = serializers.TimeField(read_only=True)

    class Meta:
        model = TransportAllocation
        fields = '__all__'
        read_only_fields = ['id', 'pickup_time', 'drop_time']

class TransportAttendanceSerializer(TenantAwareSerializer):
    marked_by_detail = RelatedFieldAlternative(
        source='marked_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    
    # Student Info
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = TransportAttendance
        fields = '__all__'

# ============================================================================
# MAINTENANCE & OPS SERIALIZERS
# ============================================================================

class MaintenanceRecordSerializer(TenantAwareSerializer):
    vehicle_detail = RelatedFieldAlternative(
        source='vehicle',
        read_only=True,
        serializer=VehicleSerializer
    )

    class Meta:
        model = MaintenanceRecord
        fields = '__all__'
        ref_name = "TransportationMaintenanceRecord"

class FuelRecordSerializer(TenantAwareSerializer):
    vehicle_detail = RelatedFieldAlternative(
        source='vehicle',
        read_only=True,
        serializer=VehicleSerializer
    )
    
    # Computed
    mileage = serializers.FloatField(read_only=True)

    class Meta:
        model = FuelRecord
        fields = '__all__'
        read_only_fields = ['id', 'mileage']
