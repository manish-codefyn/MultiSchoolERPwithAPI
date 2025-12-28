from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from apps.core.api.views import BaseAPIView
from apps.hostel.models import Hostel, Room, HostelAllocation, HostelAttendance

class HostelDashboardAPIView(BaseAPIView):
    """
    API View to provide summary statistics for the Hostel Dashboard
    """
    roles_required = ['admin', 'principal', 'vice_principal', 'warden']
    
    def get(self, request, *args, **kwargs):
        tenant = request.tenant
        today = timezone.now().date()

        # 1. Hostel Overview
        all_hostels = Hostel.objects.filter(tenant=tenant)
        total_hostels = all_hostels.count()
        total_capacity = 0
        total_occupancy = 0
        
        for hostel in all_hostels:
            total_capacity += hostel.total_capacity
            total_occupancy += hostel.current_occupancy

        # 2. Rooms
        total_rooms = Room.objects.filter(tenant=tenant).count()
        
        # 3. Allocations
        active_allocations = HostelAllocation.objects.filter(tenant=tenant, is_active=True).count()
        
        # 4. Attendance Today
        attendance_today = HostelAttendance.objects.filter(tenant=tenant, date=today)
        present_count = attendance_today.filter(status='PRESENT').count()
        absent_count = attendance_today.filter(status='ABSENT').count()
        
        occupancy_rate = 0
        if total_capacity > 0:
            occupancy_rate = (total_occupancy / total_capacity) * 100

        data = {
            "stats": [
                {
                    "label": "Total Hostels",
                    "value": str(total_hostels),
                    "sub_label": f"{total_rooms} Rooms",
                    "icon": "hotel",
                    "color": "#673AB7" # Deep Purple
                },
                {
                    "label": "Total Students",
                    "value": str(active_allocations),
                    "sub_label": "Residents",
                    "icon": "person",
                    "color": "#3F51B5" # Indigo
                },
                {
                    "label": "Occupancy",
                    "value": f"{occupancy_rate:.1f}%",
                    "sub_label": f"{total_capacity - total_occupancy} Beds Free",
                    "icon": "pie_chart",
                    "color": "#009688" # Teal
                },
                {
                    "label": "Present Today",
                    "value": str(present_count),
                    "sub_label": f"{absent_count} Absent",
                    "icon": "how_to_reg",
                    "color": "#4CAF50" # Green
                }
            ],
            "meta": {
                "total_capacity": total_capacity,
                "total_occupancy": total_occupancy
            }
        }
        
        return Response(data, status=status.HTTP_200_OK)
