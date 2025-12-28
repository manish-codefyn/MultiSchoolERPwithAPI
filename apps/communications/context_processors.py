from .models import Notification

def unread_count(request):
    """
    Context processor to add unread notification count
    """
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
