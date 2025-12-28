
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.communications.models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        print(f"DEBUG: WebSocket Connect. User: {self.user}, Authenticated: {self.user.is_authenticated}")
        
        # Only allow authenticated users
        if not self.user.is_authenticated:
            print("DEBUG: WebSocket connection rejected - Unauthenticated")
            await self.close()
            return

        # Group name based on user ID: "user_<id>"
        # Note: In multi-tenant, user IDs might collide IF they are integers and tables are separate?
        # But here User model is SHARED (in public schema) usually, or we trust UUIDs.
        # User model (apps.users.models.User) is likely UUIDModel based on previous views.
        # Let's verify UUID usage. If UUID, collision is impossible.
        
        self.group_name = f"user_{self.user.id}"

        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    # Receive message from WebSocket (not used much for simple notifications, but good for chat)
    async def receive(self, text_data):
        pass

    # Receive message from room group
    async def notification_message(self, event):
        message = event["message"]
        title = event.get("title", "New Notification")
        action_url = event.get("action_url", "#")

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "title": title,
            "message": message,
            "action_url": action_url
        }))

    async def chat_message(self, event):
        """
        Handle real-time chat messages
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": event["message"],
            "sender_name": event["sender_name"],
            "sender_id": event["sender_id"],
            "thread_id": event["thread_id"],
            "title": event["title"],
            "action_url": event["action_url"]
        }))
