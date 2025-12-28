from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.api.serializers import TenantAwareSerializer, RelatedFieldAlternative
from apps.hostel.models import (
    Amenity, Facility, Hostel, Room, HostelAllocation,
    HostelAttendance, LeaveApplication, MessMenuCategory,
    MessMenuItem, DailyMessMenu, DailyMenuItem,
    HostelMessSubscription, MessAttendance, MessFeedback
)

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
# INFRASTRUCTURE SERIALIZERS
# ============================================================================

class AmenitySerializer(TenantAwareSerializer):
    class Meta:
        model = Amenity
        fields = '__all__'

class FacilitySerializer(TenantAwareSerializer):
    class Meta:
        model = Facility
        fields = '__all__'

class HostelSerializer(TenantAwareSerializer):
    warden_detail = RelatedFieldAlternative(
        source='warden',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    amenities_detail = AmenitySerializer(source='amenities', many=True, read_only=True)
    
    # Computed
    current_occupancy = serializers.IntegerField(read_only=True)
    available_beds = serializers.IntegerField(read_only=True)
    occupancy_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = Hostel
        fields = '__all__'
        read_only_fields = ['id', 'current_occupancy', 'available_beds', 'occupancy_percentage']

class RoomSerializer(TenantAwareSerializer):
    hostel_detail = RelatedFieldAlternative(
        source='hostel',
        read_only=True,
        serializer=HostelSerializer
    )
    facilities_detail = FacilitySerializer(source='facilities', many=True, read_only=True)
    
    # Computed
    available_beds = serializers.IntegerField(read_only=True)

    class Meta:
        model = Room
        fields = '__all__'
        read_only_fields = ['id', 'available_beds']

# ============================================================================
# ACCOMMODATION SERIALIZERS
# ============================================================================

class HostelAllocationSerializer(TenantAwareSerializer):
    hostel_detail = RelatedFieldAlternative(
        source='hostel',
        read_only=True,
        serializer=HostelSerializer
    )
    room_detail = RelatedFieldAlternative(
        source='room',
        read_only=True,
        serializer=RoomSerializer
    )
    
    # Student Info
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_admission_number = serializers.CharField(source='student.admission_number', read_only=True)
    
    # Computed
    duration_stayed = serializers.IntegerField(read_only=True)

    class Meta:
        model = HostelAllocation
        fields = '__all__'
        read_only_fields = ['id', 'duration_stayed']

class HostelAttendanceSerializer(TenantAwareSerializer):
    marked_by_detail = RelatedFieldAlternative(
        source='marked_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    
    # Student Info
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = HostelAttendance
        fields = '__all__'

class LeaveApplicationSerializer(TenantAwareSerializer):
    approved_by_detail = RelatedFieldAlternative(
        source='approved_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    
    # Student Info
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    # Computed
    duration_hours = serializers.FloatField(read_only=True)

    class Meta:
        model = LeaveApplication
        fields = '__all__'
        ref_name = "HostelLeaveApplication"
        read_only_fields = ['id', 'duration_hours']

# ============================================================================
# MESS SERIALIZERS
# ============================================================================

class MessMenuCategorySerializer(TenantAwareSerializer):
    class Meta:
        model = MessMenuCategory
        fields = '__all__'

class MessMenuItemSerializer(TenantAwareSerializer):
    category_detail = RelatedFieldAlternative(
        source='category',
        read_only=True,
        serializer=MessMenuCategorySerializer
    )

    class Meta:
        model = MessMenuItem
        fields = '__all__'

class DailyMenuItemSerializer(TenantAwareSerializer):
    menu_item_detail = RelatedFieldAlternative(
        source='menu_item',
        read_only=True,
        serializer=MessMenuItemSerializer
    )
    
    # Computed
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = DailyMenuItem
        fields = '__all__'
        read_only_fields = ['id', 'final_price', 'is_available']

class DailyMessMenuSerializer(TenantAwareSerializer):
    # Detailed items through the intermediate model
    menu_items_detail = DailyMenuItemSerializer(source='menu_items', many=True, read_only=True)

    class Meta:
        model = DailyMessMenu
        fields = '__all__'

class HostelMessSubscriptionSerializer(TenantAwareSerializer):
    # Student Info
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = HostelMessSubscription
        fields = '__all__'

class MessAttendanceSerializer(TenantAwareSerializer):
    daily_menu_detail = RelatedFieldAlternative(
        source='daily_menu',
        read_only=True,
        serializer=DailyMessMenuSerializer
    )
    
    # Student Info
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = MessAttendance
        fields = '__all__'

class MessFeedbackSerializer(TenantAwareSerializer):
    daily_menu_detail = RelatedFieldAlternative(
        source='daily_menu',
        read_only=True,
        serializer=DailyMessMenuSerializer
    )
    
    # Student Info
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = MessFeedback
        fields = '__all__'
