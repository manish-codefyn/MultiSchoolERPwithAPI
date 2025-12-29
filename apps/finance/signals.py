from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment
from apps.communications.models import Notification

@receiver(post_save, sender=Payment)
def payment_notification(sender, instance, created, **kwargs):
    """
    Send notification when payment is completed
    """
    if instance.status == 'COMPLETED' and instance.student and instance.student.user:
        # Create Notification Record
        notification = Notification.objects.create(
            recipient=instance.student.user,
            title="Payment Received",
            message=f"We have received your payment of ₹{instance.amount} for Invoice #{instance.invoice.invoice_number}.",
            notification_type='FINANCIAL',
            priority='HIGH',
            action_url=f"/portal/finance/invoices/",
            action_text="View Invoice"
        )
        
        # Send Real-time Notification
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.student.user.id}",
            {
                "type": "notification_message",
                "title": notification.title,
                "message": notification.message,
                "action_url": notification.action_url
            }
        )
