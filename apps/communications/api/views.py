from rest_framework import status
from rest_framework.response import Response
from apps.core.api.views import (
    BaseListCreateAPIView, BaseRetrieveUpdateDestroyAPIView
)
from apps.communications.models import (
    CommunicationChannel, CommunicationTemplate, CommunicationCampaign,
    Communication, CommunicationAttachment
)
from apps.communications.api.serializers import (
    CommunicationChannelSerializer, CommunicationTemplateSerializer,
    CommunicationCampaignSerializer, CommunicationSerializer,
    CommunicationAttachmentSerializer,
    # Messaging & Notification
    MessageThreadSerializer, MessageSerializer, NotificationSerializer
)

from django.db.models import Count, Q
from django.utils import timezone
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from rest_framework import views
from apps.communications.models import (
    MessageThread, Message, MessageRecipient, Notification
)

# ============================================================================
# CONFIG VIEWS
# ============================================================================

class CommunicationChannelListCreateAPIView(BaseListCreateAPIView):
    model = CommunicationChannel
    serializer_class = CommunicationChannelSerializer
    search_fields = ['name', 'code']
    filterset_fields = ['channel_type', 'is_active', 'is_healthy']
    roles_required = ['admin', 'communications_manager']

class CommunicationChannelDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = CommunicationChannel
    serializer_class = CommunicationChannelSerializer
    roles_required = ['admin', 'communications_manager']


class CommunicationTemplateListCreateAPIView(BaseListCreateAPIView):
    model = CommunicationTemplate
    serializer_class = CommunicationTemplateSerializer
    search_fields = ['name', 'code', 'subject']
    filterset_fields = ['channel', 'template_type', 'language', 'is_active', 'is_approved']
    roles_required = ['admin', 'communications_manager', 'teacher']

class CommunicationTemplateDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = CommunicationTemplate
    serializer_class = CommunicationTemplateSerializer
    roles_required = ['admin', 'communications_manager']

# ============================================================================
# CAMPAIGN VIEWS
# ============================================================================

class CommunicationCampaignListCreateAPIView(BaseListCreateAPIView):
    model = CommunicationCampaign
    serializer_class = CommunicationCampaignSerializer
    search_fields = ['name']
    filterset_fields = ['campaign_type', 'status', 'template']
    roles_required = ['admin', 'communications_manager']

class CommunicationCampaignDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = CommunicationCampaign
    serializer_class = CommunicationCampaignSerializer
    roles_required = ['admin', 'communications_manager']

# ============================================================================
# COMMUNICATION VIEWS
# ============================================================================

class CommunicationListCreateAPIView(BaseListCreateAPIView):
    model = Communication
    serializer_class = CommunicationSerializer
    search_fields = ['title', 'subject', 'external_recipient_email']
    filterset_fields = ['channel', 'template', 'campaign', 'status', 'direction', 'priority']
    roles_required = ['admin', 'communications_manager', 'teacher']

class CommunicationDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Communication
    serializer_class = CommunicationSerializer
    roles_required = ['admin', 'communications_manager']


class CommunicationAttachmentListCreateAPIView(BaseListCreateAPIView):
    model = CommunicationAttachment
    serializer_class = CommunicationAttachmentSerializer
    search_fields = ['file_name']
    filterset_fields = ['communication', 'file_type']
    roles_required = ['admin', 'communications_manager']

class CommunicationAttachmentDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = CommunicationAttachment
    serializer_class = CommunicationAttachmentSerializer
    roles_required = ['admin', 'communications_manager']

# ============================================================================
# MESSAGING VIEWS
# ============================================================================

class MessageThreadListCreateAPIView(BaseListCreateAPIView):
    model = MessageThread
    serializer_class = MessageThreadSerializer
    search_fields = ['title']
    filterset_fields = ['is_active']
    roles_required = ['admin', 'communications_manager', 'teacher', 'student', 'parent']

    def get_queryset(self):
        return MessageThread.objects.filter(
            participants=self.request.user,
            is_active=True
        ).prefetch_related('participants', 'messages').annotate(
            unread_count=Count(
                'messages',
                filter=Q(messages__recipients__recipient=self.request.user, messages__recipients__is_read=False)
            )
        ).order_by('-last_message_at')

    def perform_create(self, serializer):
        thread = serializer.save(created_by=self.request.user)
        thread.participants.add(self.request.user)
        # Note: Additional participants must be passed in 'participants' field of serializer

class MessageThreadDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = MessageThread
    serializer_class = MessageThreadSerializer
    roles_required = ['admin', 'communications_manager', 'teacher', 'student', 'parent']

    def get_queryset(self):
         return MessageThread.objects.filter(participants=self.request.user)

class MessageListCreateAPIView(BaseListCreateAPIView):
    model = Message
    serializer_class = MessageSerializer
    search_fields = ['body']
    roles_required = ['admin', 'communications_manager', 'teacher', 'student', 'parent']

    def get_queryset(self):
        thread_id = self.kwargs.get('pk')
        return Message.objects.filter(
            thread_id=thread_id,
            thread__participants=self.request.user
        ).select_related('sender').order_by('created_at')

    def perform_create(self, serializer):
        thread_id = self.kwargs.get('pk')
        try:
            thread = MessageThread.objects.get(id=thread_id, participants=self.request.user)
        except MessageThread.DoesNotExist:
             from rest_framework.exceptions import NotFound
             raise NotFound("Thread not found")
             
        message = serializer.save(sender=self.request.user, thread=thread)
        
        # Update thread timestamp
        thread.last_message_at = timezone.now()
        thread.save()

        # Create Recipients & Notifications
        participants = thread.participants.exclude(id=self.request.user.id)
        for participant in participants:
             MessageRecipient.objects.create(message=message, recipient=participant)
             
             action_url = self.request.build_absolute_uri(reverse('communications:thread_detail', kwargs={'pk': thread.id}))
             
             Notification.objects.create(
                tenant=self.request.tenant,
                recipient=participant,
                title=f"New Message in {thread.title[:30]}...",
                message=f"{self.request.user.get_full_name()} sent a message",
                notification_type="MESSAGE",
                priority="MEDIUM",
                content_type=ContentType.objects.get_for_model(thread),
                object_id=thread.id,
                action_url=action_url
            )

# ============================================================================
# NOTIFICATION VIEWS
# ============================================================================

class NotificationListAPIView(BaseListCreateAPIView):
    model = Notification
    serializer_class = NotificationSerializer
    search_fields = ['title', 'message']
    filterset_fields = ['is_read', 'notification_type', 'priority']
    roles_required = ['admin', 'communications_manager', 'teacher', 'student', 'parent']

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

class NotificationDetailAPIView(BaseRetrieveUpdateDestroyAPIView):
    model = Notification
    serializer_class = NotificationSerializer
    roles_required = ['admin', 'communications_manager', 'teacher', 'student', 'parent']
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

class MarkAllNotificationsReadAPIView(views.APIView):
    def post(self, request, *args, **kwargs):
        Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return Response({'status': 'success'})
