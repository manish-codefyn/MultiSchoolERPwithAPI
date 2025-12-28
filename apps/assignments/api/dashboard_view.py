from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from apps.core.api.views import BaseAPIView
from apps.assignments.models import Assignment, Submission

class AssignmentsDashboardAPIView(BaseAPIView):
    """
    API View to provide summary statistics for the Assignments Dashboard
    """
    roles_required = ['admin', 'principal', 'vice_principal', 'teacher', 'student']
    
    def get(self, request, *args, **kwargs):
        tenant = request.tenant
        today = timezone.now().date()
        
        # 1. Assignment Stats
        all_assignments = Assignment.objects.filter(tenant=tenant)
        active_assignments = all_assignments.filter(due_date__gte=timezone.now()).count()
        total_assignments = all_assignments.count()
        
        # 2. Submission Stats
        all_submissions = Submission.objects.filter(tenant=tenant)
        pending_grading = all_submissions.filter(status='SUBMITTED').count()
        submitted_today = all_submissions.filter(submitted_at__date=today).count()

        # 3. Recent Assignments (Active)
        recent_assignments_qs = all_assignments.filter(due_date__gte=timezone.now()).order_by('due_date')[:5]
        recent_assignments = []
        for assign in recent_assignments_qs:
            recent_assignments.append({
                "title": assign.title,
                "subject": assign.subject.name,
                "due_date": assign.due_date.strftime("%Y-%m-%d"),
                "class": str(assign.class_name),
            })

        data = {
            "stats": [
                {
                    "label": "Active",
                    "value": str(active_assignments),
                    "sub_label": "Due Soon",
                    "icon": "assignment",
                    "color": "#2196F3" # Blue
                },
                {
                    "label": "Pending Grading",
                    "value": str(pending_grading),
                    "sub_label": "To Review",
                    "icon": "rate_review",
                    "color": "#FF9800" # Orange
                },
                {
                    "label": "Submitted Today",
                    "value": str(submitted_today),
                    "sub_label": "New Work",
                    "icon": "today",
                    "color": "#4CAF50" # Green
                },
                {
                    "label": "Total",
                    "value": str(total_assignments),
                    "sub_label": "All Time",
                    "icon": "folder",
                    "color": "#9C27B0" # Purple
                }
            ],
            "recent_assignments": recent_assignments
        }
        
        return Response(data, status=status.HTTP_200_OK)
