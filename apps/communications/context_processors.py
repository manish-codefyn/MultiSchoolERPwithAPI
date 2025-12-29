from .models import Notification

def unread_count(request):
    """
    Context processor to add unread notification count
    """
    # Avoid querying tenant-specific tables on public schema
    if hasattr(request, 'tenant') and request.tenant.schema_name == 'public':
        return {
            'unread_notification_count': 0,
            'header_notifications': []
        }

    if request.user.is_authenticated:
        qs = Notification.objects.filter(recipient=request.user)
        count = qs.filter(is_read=False).count()
        latest = qs.order_by('-created_at')[:5]
        
        return {
            'unread_notification_count': count,
            'header_notifications': latest
        }
    return {
        'unread_notification_count': 0, 
        'header_notifications': []
    }
