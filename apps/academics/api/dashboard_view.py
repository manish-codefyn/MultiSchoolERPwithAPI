from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from apps.core.api.views import BaseAPIView
from apps.academics.models import SchoolClass, Section, Subject, House, AcademicYear, ClassSubject

class AcademicsDashboardAPIView(BaseAPIView):
    """
    API View to provide summary statistics for the Academics Dashboard
    """
    roles_required = ['admin', 'principal', 'vice_principal', 'academic_coordinator']
    
    def get(self, request, *args, **kwargs):
        tenant = request.tenant
        
        # 1. Total Classes & Sections
        total_classes = SchoolClass.objects.filter(
            tenant=tenant, is_active=True
        ).count()
        
        total_sections = Section.objects.filter(
            tenant=tenant, is_active=True
        ).count()
        
        # 2. Subjects
        total_subjects = Subject.objects.filter(
            tenant=tenant, is_active=True
        ).count()
        
        # 3. Houses
        total_houses = House.objects.filter(
            tenant=tenant
        ).count()
        
        # 4. Academic Years info
        current_year = AcademicYear.objects.filter(
            tenant=tenant, is_current=True
        ).first()
        
        current_year_name = current_year.name if current_year else "N/A"
        
        # 5. Teacher Assignment Stats (How many active class subjects have teachers assigned)
        assigned_subjects = ClassSubject.objects.filter(
            tenant=tenant, 
            academic_year=current_year,
            teacher__isnull=False
        ).count() if current_year else 0
        
        total_assigned_slots = ClassSubject.objects.filter(
             tenant=tenant,
             academic_year=current_year
        ).count() if current_year else 0
        
        
        data = {
            "stats": [
                {
                    "label": "Total Classes",
                    "value": str(total_classes),
                    "icon": "class_outlined",
                    "color": "#4CAF50" # Green
                },
                 {
                    "label": "Total Sections",
                    "value": str(total_sections),
                    "icon": "grid_view",
                    "color": "#2196F3" # Blue
                },
                {
                    "label": "Subjects",
                    "value": str(total_subjects),
                    "icon": "book_outlined",
                    "color": "#FF9800" # Orange
                },
                {
                    "label": "Houses",
                    "value": str(total_houses),
                    "icon": "house_outlined",
                    "color": "#9C27B0" # Purple
                }
            ],
            "meta": {
                "current_academic_year": current_year_name,
                "teacher_coverage": f"{assigned_subjects}/{total_assigned_slots}"
            }
        }
        
        return Response(data, status=status.HTTP_200_OK)
