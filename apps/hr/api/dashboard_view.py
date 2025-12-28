from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Count
from apps.core.api.views import BaseAPIView
from apps.hr.models import Staff, Department, StaffAttendance, LeaveApplication

class StaffDashboardAPIView(BaseAPIView):
    """
    API View to provide summary statistics for the Staff (HR) Dashboard
    """
    roles_required = ['admin', 'principal', 'vice_principal', 'hr_manager']
    
    def get(self, request, *args, **kwargs):
        tenant = request.tenant
        today = timezone.now().date()

        # 1. Staff Counts
        all_staff = Staff.objects.filter(tenant=tenant)
        total_staff = all_staff.count()
        active_staff = all_staff.filter(employment_status='ACTIVE').count()
        
        # 2. Teaching vs Non-Teaching
        # Assuming we can determine this by designation or role
        # Using a simpler check if `is_teaching_staff` logic is replicable or checking user role
        # Staff model has `is_teaching_staff` property but we filter on user__role in helper usually
        # Let's count by User role if linked
        teaching_staff = all_staff.filter(user__role='teacher', employment_status='ACTIVE').count()
        support_staff = active_staff - teaching_staff
        
        # 3. Department Stats
        departments_count = Department.objects.filter(tenant=tenant).count()
        
        # 4. Attendance Today
        attendance_today = StaffAttendance.objects.filter(tenant=tenant, date=today)
        present_count = attendance_today.filter(status__in=['PRESENT', 'LATE', 'HALF_DAY']).count()
        absent_count = attendance_today.filter(status='ABSENT').count()
        on_leave_today = attendance_today.filter(status='LEAVE').count()
        
        # 5. Pending Leave Applications
        pending_leaves = LeaveApplication.objects.filter(tenant=tenant, status='PENDING').count()
        
        data = {
            "stats": [
                {
                    "label": "Total Staff",
                    "value": str(total_staff),
                    "sub_label": f"{active_staff} Active",
                    "icon": "group",
                    "color": "#3F51B5" # Indigo
                },
                {
                    "label": "Present Today",
                    "value": str(present_count),
                    "sub_label": f"Absent: {absent_count}",
                    "icon": "event_available",
                    "color": "#4CAF50" # Green
                },
                 {
                    "label": "On Leave",
                    "value": str(on_leave_today),
                    "sub_label": f"{pending_leaves} Pending Req",
                    "icon": "beach_access",
                    "color": "#FF9800" # Orange
                },
                {
                    "label": "Departments",
                    "value": str(departments_count),
                    "sub_label": "Organization",
                    "icon": "domain",
                    "color": "#607D8B" # Blue Grey
                }
            ],
             "meta": {
                "teaching_staff": teaching_staff,
                "support_staff": support_staff
            }
        }
        
        return Response(data, status=status.HTTP_200_OK)
