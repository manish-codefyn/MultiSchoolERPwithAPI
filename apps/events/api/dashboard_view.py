from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from apps.core.api.views import BaseAPIView
from apps.events.models import Event, EventRegistration

class EventsDashboardAPIView(BaseAPIView):
    """
    API View to provide summary statistics for the Events Dashboard
    """
    roles_required = ['admin', 'principal', 'vice_principal', 'teacher', 'student', 'parent']
    
    def get(self, request, *args, **kwargs):
        tenant = request.tenant
        today = timezone.now().date()

        # 1. Event Counts
        all_events = Event.objects.filter(tenant=tenant)
        total_events = all_events.count()
        
        upcoming_events = all_events.filter(start_date__gt=today).count()
        ongoing_events = all_events.filter(status='ONGOING').count()
        completed_events = all_events.filter(status='COMPLETED').count()

        # 2. Registrations
        total_registrations = EventRegistration.objects.filter(tenant=tenant, status='REGISTERED').count()
        
        # 3. Next Upcoming Event
        next_event_obj = all_events.filter(start_date__gte=today).order_by('start_date').first()
        next_event = None
        if next_event_obj:
            next_event = {
                "title": next_event_obj.title,
                "date": next_event_obj.start_date.strftime("%Y-%m-%d"),
                "venue": next_event_obj.venue
            }

        data = {
            "stats": [
                {
                    "label": "Total Events",
                    "value": str(total_events),
                    "sub_label": "Lifetime",
                    "icon": "event",
                    "color": "#9C27B0" # Purple
                },
                {
                    "label": "Upcoming",
                    "value": str(upcoming_events),
                    "sub_label": "Scheduled",
                    "icon": "upcoming",
                    "color": "#2196F3" # Blue
                },
                {
                    "label": "Ongoing",
                    "value": str(ongoing_events),
                    "sub_label": "Active Now",
                    "icon": "campaign",
                    "color": "#4CAF50" # Green
                },
                {
                    "label": "Registrations",
                    "value": str(total_registrations),
                    "sub_label": "Participants",
                    "icon": "how_to_reg",
                    "color": "#FF9800" # Orange
                }
            ],
            "next_event": next_event
        }
        
        return Response(data, status=status.HTTP_200_OK)
