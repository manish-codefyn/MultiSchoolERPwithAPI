
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification, MessageRecipient

@receiver(post_save, sender=Notification)
def send_notification_socket(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        group_name = f"user_{instance.recipient.id}"
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "notification_message",
                "message": instance.message,
                "title": instance.title,
                "action_url": instance.action_url or "#"
            }
        )

@receiver(post_save, sender=MessageRecipient)
def send_message_socket(sender, instance, created, **kwargs):
    if created:
        print(f"DEBUG: Signal fired for MessageRecipient: {instance.id} to {instance.recipient.email}")
        channel_layer = get_channel_layer()
        group_name = f"user_{instance.recipient.id}"
        
        # Construct action URL
        thread_id = instance.message.thread_id
        action_url = f"/communications/inbox/{thread_id}/" if thread_id else "#"
        
        try:
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "chat_message", # Custom handler in consumer
                    "message": instance.message.body,
                    "sender_name": instance.message.sender.get_full_name(),
                    "sender_id": str(instance.message.sender.id), # Ensure string for serialization
                    "thread_id": str(thread_id) if thread_id else None,
                    "title": f"New Message from {instance.message.sender.get_full_name()}",
                    "action_url": action_url
                }
            )
            print(f"DEBUG: Message sent to group {group_name}")
        except Exception as e:
            print(f"DEBUG: Error sending message to socket: {e}")
