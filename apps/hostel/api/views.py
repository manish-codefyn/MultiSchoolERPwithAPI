from rest_framework import status
from rest_framework.response import Response
from apps.core.api.views import (
    BaseListCreateAPIView, BaseRetrieveUpdateDestroyAPIView
)
from apps.hostel.models import (
    Amenity, Facility, Hostel, Room, HostelAllocation,
    HostelAttendance, LeaveApplication, MessMenuCategory,
    MessMenuItem, DailyMessMenu, DailyMenuItem,
    HostelMessSubscription, MessAttendance, MessFeedback
)
from apps.hostel.api.serializers import (
    AmenitySerializer, FacilitySerializer, HostelSerializer,
    RoomSerializer, HostelAllocationSerializer, HostelAttendanceSerializer,
    LeaveApplicationSerializer, MessMenuCategorySerializer,
    MessMenuItemSerializer, DailyMessMenuSerializer, DailyMenuItemSerializer,
    HostelMessSubscriptionSerializer, MessAttendanceSerializer,
    MessFeedbackSerializer
)

# ============================================================================
# INFRASTRUCTURE VIEWS
# ============================================================================

class AmenityListCreateAPIView(BaseListCreateAPIView):
    model = Amenity
    serializer_class = AmenitySerializer
    roles_required = ['admin', 'hostel_manager']

class AmenityDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Amenity
    serializer_class = AmenitySerializer
    roles_required = ['admin', 'hostel_manager']


class FacilityListCreateAPIView(BaseListCreateAPIView):
    model = Facility
    serializer_class = FacilitySerializer
    roles_required = ['admin', 'hostel_manager']

class FacilityDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Facility
    serializer_class = FacilitySerializer
    roles_required = ['admin', 'hostel_manager']


class HostelListCreateAPIView(BaseListCreateAPIView):
    model = Hostel
    serializer_class = HostelSerializer
    search_fields = ['name', 'code', 'warden__first_name']
    filterset_fields = ['hostel_type', 'is_active']
    roles_required = ['admin', 'hostel_manager', 'student', 'parent']

class HostelDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Hostel
    serializer_class = HostelSerializer
    roles_required = ['admin', 'hostel_manager']


class RoomListCreateAPIView(BaseListCreateAPIView):
    model = Room
    serializer_class = RoomSerializer
    search_fields = ['room_number', 'hostel__name']
    filterset_fields = ['hostel', 'room_type', 'floor', 'is_available']
    roles_required = ['admin', 'hostel_manager', 'student', 'parent']

class RoomDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Room
    serializer_class = RoomSerializer
    roles_required = ['admin', 'hostel_manager']

# ============================================================================
# ALLOCATION & ATTENDANCE VIEWS
# ============================================================================

class HostelAllocationListCreateAPIView(BaseListCreateAPIView):
    model = HostelAllocation
    serializer_class = HostelAllocationSerializer
    search_fields = ['student__first_name', 'student__admission_number', 'room__room_number']
    filterset_fields = ['hostel', 'room', 'is_active', 'student']
    roles_required = ['admin', 'hostel_manager']

class HostelAllocationDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = HostelAllocation
    serializer_class = HostelAllocationSerializer
    roles_required = ['admin', 'hostel_manager']


class HostelAttendanceListCreateAPIView(BaseListCreateAPIView):
    model = HostelAttendance
    serializer_class = HostelAttendanceSerializer
    filterset_fields = ['date', 'status', 'student']
    roles_required = ['admin', 'hostel_manager', 'warden']

class HostelAttendanceDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = HostelAttendance
    serializer_class = HostelAttendanceSerializer
    roles_required = ['admin', 'hostel_manager', 'warden']


class LeaveApplicationListCreateAPIView(BaseListCreateAPIView):
    model = LeaveApplication
    serializer_class = LeaveApplicationSerializer
    search_fields = ['student__first_name']
    filterset_fields = ['status', 'leave_type', 'student']
    roles_required = ['admin', 'hostel_manager', 'student', 'parent']

class LeaveApplicationDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = LeaveApplication
    serializer_class = LeaveApplicationSerializer
    roles_required = ['admin', 'hostel_manager', 'warden']

# ============================================================================
# MESS VIEWS
# ============================================================================

class MessMenuCategoryListCreateAPIView(BaseListCreateAPIView):
    model = MessMenuCategory
    serializer_class = MessMenuCategorySerializer
    roles_required = ['admin', 'hostel_manager']

class MessMenuCategoryDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = MessMenuCategory
    serializer_class = MessMenuCategorySerializer
    roles_required = ['admin', 'hostel_manager']


class MessMenuItemListCreateAPIView(BaseListCreateAPIView):
    model = MessMenuItem
    serializer_class = MessMenuItemSerializer
    search_fields = ['name']
    filterset_fields = ['category', 'food_type', 'is_available']
    roles_required = ['admin', 'hostel_manager']

class MessMenuItemDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = MessMenuItem
    serializer_class = MessMenuItemSerializer
    roles_required = ['admin', 'hostel_manager']


class DailyMessMenuListCreateAPIView(BaseListCreateAPIView):
    model = DailyMessMenu
    serializer_class = DailyMessMenuSerializer
    filterset_fields = ['date', 'day', 'meal']
    roles_required = ['admin', 'hostel_manager', 'student']

class DailyMessMenuDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = DailyMessMenu
    serializer_class = DailyMessMenuSerializer
    roles_required = ['admin', 'hostel_manager']


class DailyMenuItemListCreateAPIView(BaseListCreateAPIView):
    model = DailyMenuItem
    serializer_class = DailyMenuItemSerializer
    filterset_fields = ['daily_menu']
    roles_required = ['admin', 'hostel_manager', 'student']

class DailyMenuItemDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = DailyMenuItem
    serializer_class = DailyMenuItemSerializer
    roles_required = ['admin', 'hostel_manager']


class HostelMessSubscriptionListCreateAPIView(BaseListCreateAPIView):
    model = HostelMessSubscription
    serializer_class = HostelMessSubscriptionSerializer
    search_fields = ['student__first_name']
    filterset_fields = ['plan_type', 'is_active', 'student']
    roles_required = ['admin', 'hostel_manager']

class HostelMessSubscriptionDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = HostelMessSubscription
    serializer_class = HostelMessSubscriptionSerializer
    roles_required = ['admin', 'hostel_manager']


class MessAttendanceListCreateAPIView(BaseListCreateAPIView):
    model = MessAttendance
    serializer_class = MessAttendanceSerializer
    filterset_fields = ['student', 'daily_menu']
    roles_required = ['admin', 'hostel_manager']

class MessAttendanceDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = MessAttendance
    serializer_class = MessAttendanceSerializer
    roles_required = ['admin', 'hostel_manager']


class MessFeedbackListCreateAPIView(BaseListCreateAPIView):
    model = MessFeedback
    serializer_class = MessFeedbackSerializer
    roles_required = ['admin', 'hostel_manager', 'student']

class MessFeedbackDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = MessFeedback
    serializer_class = MessFeedbackSerializer
    roles_required = ['admin', 'hostel_manager']
