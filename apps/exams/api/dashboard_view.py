from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from apps.core.api.views import BaseAPIView
from apps.exams.models import Exam, ExamResult

class ExamsDashboardAPIView(BaseAPIView):
    """
    API View to provide summary statistics for the Exams Dashboard
    """
    roles_required = ['admin', 'principal', 'vice_principal', 'teacher', 'student', 'parent']
    
    def get(self, request, *args, **kwargs):
        tenant = request.tenant
        today = timezone.now().date()

        # 1. Exam Stats
        all_exams = Exam.objects.filter(tenant=tenant)
        total_exams = all_exams.count()
        ongoing_exams = all_exams.filter(status='ONGOING').count()
        upcoming_exams = all_exams.filter(start_date__gt=today).count()
        
        # 2. Results Info
        published_results = all_exams.filter(is_published=True).count() # Or status='COMPLETED'

        # 3. Next Exam
        next_exam_obj = all_exams.filter(start_date__gte=today).order_by('start_date').first()
        next_exam = None
        if next_exam_obj:
            next_exam = {
                "name": next_exam_obj.name,
                "date": next_exam_obj.start_date.strftime("%Y-%m-%d"),
                "class": str(next_exam_obj.class_name),
            }

        data = {
            "stats": [
                {
                    "label": "Total Exams",
                    "value": str(total_exams),
                    "sub_label": "Conducting",
                    "icon": "assignment",
                    "color": "#673AB7" # Deep Purple
                },
                {
                    "label": "Ongoing",
                    "value": str(ongoing_exams),
                    "sub_label": "Active Now",
                    "icon": "timelapse",
                    "color": "#FFC107" # Amber
                },
                {
                    "label": "Upcoming",
                    "value": str(upcoming_exams),
                    "sub_label": "Scheduled",
                    "icon": "event_note",
                    "color": "#03A9F4" # Light Blue
                },
                {
                    "label": "Results",
                    "value": str(published_results),
                    "sub_label": "Published",
                    "icon": "grade",
                    "color": "#4CAF50" # Green
                }
            ],
            "next_exam": next_exam
        }
        
        return Response(data, status=status.HTTP_200_OK)
