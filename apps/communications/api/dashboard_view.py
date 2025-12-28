from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from apps.core.api.views import BaseAPIView
from apps.communications.models import Communication, CommunicationCampaign

class CommunicationsDashboardAPIView(BaseAPIView):
    """
    API View to provide summary statistics for the Communications Dashboard
    """
    roles_required = ['admin', 'principal', 'vice_principal', 'teacher']
    
    def get(self, request, *args, **kwargs):
        tenant = request.tenant
        
        # 1. Communication Stats
        all_comms = Communication.objects.filter(tenant=tenant)
        sent_messages = all_comms.filter(status='SENT').count()
        delivered_messages = all_comms.filter(status='DELIVERED').count()
        failed_messages = all_comms.filter(status='FAILED').count()
        
        # 2. Campaign Stats
        active_campaigns = CommunicationCampaign.objects.filter(tenant=tenant, status='RUNNING').count()

        # 3. Recent Messages
        recent_messages_qs = all_comms.order_by('-created_at')[:5]
        recent_messages = []
        for msg in recent_messages_qs:
            recent_messages.append({
                "title": msg.title,
                "status": msg.status,
                "date": msg.created_at.strftime("%Y-%m-%d %H:%M"),
                "channel": msg.channel.name if msg.channel else "Unknown"
            })

        data = {
            "stats": [
                {
                    "label": "Sent Messages",
                    "value": str(sent_messages),
                    "sub_label": "Total Sent",
                    "icon": "send",
                    "color": "#2196F3" # Blue
                },
                {
                    "label": "Delivered",
                    "value": str(delivered_messages),
                    "sub_label": "Successfully",
                    "icon": "mark_email_read",
                    "color": "#4CAF50" # Green
                },
                {
                    "label": "Failed",
                    "value": str(failed_messages),
                    "sub_label": "Errors",
                    "icon": "error",
                    "color": "#F44336" # Red
                },
                {
                    "label": "Active Campaigns",
                    "value": str(active_campaigns),
                    "sub_label": "Running Now",
                    "icon": "campaign",
                    "color": "#FF9800" # Orange
                }
            ],
            "recent_messages": recent_messages
        }
        
        return Response(data, status=status.HTTP_200_OK)
