from rest_framework import status
from rest_framework.response import Response
from apps.core.api.views import (
    BaseListCreateAPIView, BaseRetrieveUpdateDestroyAPIView
)
from apps.transportation.models import (
    Vehicle, Route, RouteStop, TransportAllocation,
    TransportAttendance, MaintenanceRecord, FuelRecord
)
from apps.transportation.api.serializers import (
    VehicleSerializer, RouteSerializer, RouteStopSerializer,
    TransportAllocationSerializer, TransportAttendanceSerializer,
    MaintenanceRecordSerializer, FuelRecordSerializer
)

# ============================================================================
# FLEET VIEWS
# ============================================================================

class VehicleListCreateAPIView(BaseListCreateAPIView):
    model = Vehicle
    serializer_class = VehicleSerializer
    search_fields = ['vehicle_number', 'registration_number', 'driver__first_name']
    filterset_fields = ['vehicle_type', 'fuel_type', 'is_active', 'under_maintenance']
    roles_required = ['admin', 'transport_manager', 'driver']

class VehicleDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Vehicle
    serializer_class = VehicleSerializer
    roles_required = ['admin', 'transport_manager']


class RouteListCreateAPIView(BaseListCreateAPIView):
    model = Route
    serializer_class = RouteSerializer
    search_fields = ['name', 'code', 'start_point', 'end_point']
    filterset_fields = ['vehicle', 'driver', 'is_active']
    roles_required = ['admin', 'transport_manager', 'driver', 'student', 'parent']

class RouteDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Route
    serializer_class = RouteSerializer
    roles_required = ['admin', 'transport_manager']


class RouteStopListCreateAPIView(BaseListCreateAPIView):
    model = RouteStop
    serializer_class = RouteStopSerializer
    filterset_fields = ['route']
    roles_required = ['admin', 'transport_manager', 'driver', 'student', 'parent']

class RouteStopDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = RouteStop
    serializer_class = RouteStopSerializer
    roles_required = ['admin', 'transport_manager']

# ============================================================================
# ALLOCATION & ATTENDANCE VIEWS
# ============================================================================

class TransportAllocationListCreateAPIView(BaseListCreateAPIView):
    model = TransportAllocation
    serializer_class = TransportAllocationSerializer
    search_fields = ['student__first_name', 'student__admission_number', 'route__name']
    filterset_fields = ['route', 'pickup_stop', 'drop_stop', 'is_active']
    roles_required = ['admin', 'transport_manager']

class TransportAllocationDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = TransportAllocation
    serializer_class = TransportAllocationSerializer
    roles_required = ['admin', 'transport_manager']


class TransportAttendanceListCreateAPIView(BaseListCreateAPIView):
    model = TransportAttendance
    serializer_class = TransportAttendanceSerializer
    search_fields = ['student__first_name']
    filterset_fields = ['date', 'trip_type', 'status', 'student']
    roles_required = ['admin', 'transport_manager', 'driver', 'attendant']

class TransportAttendanceDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = TransportAttendance
    serializer_class = TransportAttendanceSerializer
    roles_required = ['admin', 'transport_manager']

# ============================================================================
# MAINTENANCE & FUEL VIEWS
# ============================================================================

class MaintenanceRecordListCreateAPIView(BaseListCreateAPIView):
    model = MaintenanceRecord
    serializer_class = MaintenanceRecordSerializer
    filterset_fields = ['vehicle', 'maintenance_type', 'is_completed']
    roles_required = ['admin', 'transport_manager']

class MaintenanceRecordDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = MaintenanceRecord
    serializer_class = MaintenanceRecordSerializer
    roles_required = ['admin', 'transport_manager']


class FuelRecordListCreateAPIView(BaseListCreateAPIView):
    model = FuelRecord
    serializer_class = FuelRecordSerializer
    filterset_fields = ['vehicle', 'fuel_type', 'date']
    roles_required = ['admin', 'transport_manager']

class FuelRecordDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = FuelRecord
    serializer_class = FuelRecordSerializer
    roles_required = ['admin', 'transport_manager']
