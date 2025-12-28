from django.urls import path
from apps.transportation.api.views import (
    VehicleListCreateAPIView, VehicleDetailAPIView,
    RouteListCreateAPIView, RouteDetailAPIView,
    RouteStopListCreateAPIView, RouteStopDetailAPIView,
    TransportAllocationListCreateAPIView, TransportAllocationDetailAPIView,
    TransportAttendanceListCreateAPIView, TransportAttendanceDetailAPIView,
    MaintenanceRecordListCreateAPIView, MaintenanceRecordDetailAPIView,
    FuelRecordListCreateAPIView, FuelRecordDetailAPIView
)
from .dashboard_view import TransportDashboardAPIView


urlpatterns = [
    # Dashboard
    path('dashboard/', TransportDashboardAPIView.as_view(), name='dashboard'),

    # Vehicles
    path('vehicles/', VehicleListCreateAPIView.as_view(), name='vehicle-list'),
    path('vehicles/<uuid:pk>/', VehicleDetailAPIView.as_view(), name='vehicle-detail'),

    # Routes & Stops
    path('routes/', RouteListCreateAPIView.as_view(), name='route-list'),
    path('routes/<uuid:pk>/', RouteDetailAPIView.as_view(), name='route-detail'),
    
    path('stops/', RouteStopListCreateAPIView.as_view(), name='routestop-list'),
    path('stops/<uuid:pk>/', RouteStopDetailAPIView.as_view(), name='routestop-detail'),

    # Allocation & Attendance
    path('allocations/', TransportAllocationListCreateAPIView.as_view(), name='transportallocation-list'),
    path('allocations/<uuid:pk>/', TransportAllocationDetailAPIView.as_view(), name='transportallocation-detail'),
    
    path('attendance/', TransportAttendanceListCreateAPIView.as_view(), name='transportattendance-list'),
    path('attendance/<uuid:pk>/', TransportAttendanceDetailAPIView.as_view(), name='transportattendance-detail'),

    # Maintenance & Fuel
    path('maintenance/', MaintenanceRecordListCreateAPIView.as_view(), name='maintenancerecord-list'),
    path('maintenance/<uuid:pk>/', MaintenanceRecordDetailAPIView.as_view(), name='maintenancerecord-detail'),
    
    path('fuel/', FuelRecordListCreateAPIView.as_view(), name='fuelrecord-list'),
    path('fuel/<uuid:pk>/', FuelRecordDetailAPIView.as_view(), name='fuelrecord-detail'),
]
