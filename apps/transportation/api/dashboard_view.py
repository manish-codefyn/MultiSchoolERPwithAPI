from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from apps.core.api.views import BaseAPIView
from apps.transportation.models import Vehicle, Route, TransportAllocation, TransportAttendance

class TransportDashboardAPIView(BaseAPIView):
    """
    API View to provide summary statistics for the Transport Dashboard
    """
    roles_required = ['admin', 'principal', 'vice_principal', 'transport_manager']
    
    def get(self, request, *args, **kwargs):
        tenant = request.tenant
        today = timezone.now().date()

        # 1. Vehicle Stats
        all_vehicles = Vehicle.objects.filter(tenant=tenant)
        total_vehicles = all_vehicles.count()
        under_maintenance = all_vehicles.filter(under_maintenance=True).count()
        active_vehicles = total_vehicles - under_maintenance
        
        # 2. Routes
        total_routes = Route.objects.filter(tenant=tenant).count()
        
        # 3. Allocated Students
        active_allocations = TransportAllocation.objects.filter(tenant=tenant, is_active=True).count()
        
        # 4. Attendance Today (Pickup)
        attendance_today = TransportAttendance.objects.filter(tenant=tenant, date=today, trip_type='PICKUP')
        present_today = attendance_today.filter(status='PRESENT').count()
        
        # 5. Expiring Documents (next 30 days) - Optional advanced stat
        # For now simple counts

        data = {
            "stats": [
                {
                    "label": "Total Vehicles",
                    "value": str(total_vehicles),
                    "sub_label": f"{under_maintenance} Maintenance",
                    "icon": "directions_bus",
                    "color": "#FFC107" # Amber
                },
                {
                    "label": "Routes",
                    "value": str(total_routes),
                    "sub_label": "Active Routes",
                    "icon": "alt_route",
                    "color": "#4CAF50" # Green
                },
                {
                    "label": "Students Using",
                    "value": str(active_allocations),
                    "sub_label": "Transport",
                    "icon": "child_care",
                    "color": "#2196F3" # Blue
                },
                {
                    "label": "Picked Up Today",
                    "value": str(present_today),
                    "sub_label": "Morning Trip",
                    "icon": "check_circle_outline",
                    "color": "#9C27B0" # Purple
                }
            ],
            "meta": {
                "active_vehicles": active_vehicles
            }
        }
        
        return Response(data, status=status.HTTP_200_OK)
