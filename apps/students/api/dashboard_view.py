from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from apps.core.api.views import BaseAPIView
from apps.students.models import Student
from apps.academics.models import StudentAttendance

class StudentStatsDashboardAPIView(BaseAPIView):
    """
    API View to provide summary statistics for the Student Dashboard (Aggregate)
    """
    roles_required = ['admin', 'principal', 'vice_principal', 'academic_coordinator', 'hr_manager', 'teacher']
    
    def get(self, request, *args, **kwargs):
        tenant = request.tenant
        today = timezone.now().date()
        current_year = today.year 

        # 1. Student Counts
        total_students = Student.objects.filter(tenant=tenant).count()
        active_students = Student.objects.filter(tenant=tenant, status='ACTIVE').count()
        inactive_students = Student.objects.filter(tenant=tenant, status='INACTIVE').count()
        
        # 2. Gender Ratio
        male_students = Student.objects.filter(tenant=tenant, gender='M').count()
        female_students = Student.objects.filter(tenant=tenant, gender='F').count()
        
        # 3. New Admissions (Current Year)
        # Assuming enrollment_date or created_at is used. Using enrollment_date if available, else created_at
        new_admissions = Student.objects.filter(
            tenant=tenant, 
            enrollment_date__year=current_year
        ).count()
        
        # 4. Today's Attendance
        # Count present vs total students (active)
        # Note: This is a rough approximate if attendance hasn't been taken for all classes yet
        attendance_records = StudentAttendance.objects.filter(
            tenant=tenant,
            date=today
        )
        total_present = attendance_records.filter(status__in=['PRESENT', 'LATE', 'HALF_DAY']).count()
        total_absent = attendance_records.filter(status='ABSENT').count()
        
        # Calculate percentage based on active students (assuming all should be marked)
        attendance_percentage = 0
        if active_students > 0:
            attendance_percentage = (total_present / active_students) * 100

        data = {
            "stats": [
                {
                    "label": "Total Students",
                    "value": str(total_students),
                    "sub_label": f"{active_students} Active",
                    "icon": "people",
                    "color": "#2196F3" # Blue
                },
                {
                    "label": "Attendance Today",
                    "value": f"{total_present}",
                    "sub_label": f"{attendance_percentage:.1f}% Present",
                    "icon": "today",
                    "color": "#4CAF50" # Green
                },
                {
                    "label": "New Admissions",
                    "value": str(new_admissions),
                    "sub_label": f"Year {current_year}",
                    "icon": "person_add",
                    "color": "#FF9800" # Orange
                },
                {
                    "label": "Gender Ratio",
                    "value": f"{male_students}:{female_students}",
                    "sub_label": "M:F",
                    "icon": "wc",
                    "color": "#9C27B0" # Purple
                }
            ],
            "charts": {
                "gender_distribution": {
                    "Male": male_students,
                    "Female": female_students,
                    "Other": total_students - (male_students + female_students)
                },
                "status_distribution": {
                    "Active": active_students,
                    "Inactive": inactive_students
                }
            }
        }
        
        return Response(data, status=status.HTTP_200_OK)
