from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.api.serializers import TenantAwareSerializer, RelatedFieldAlternative
from apps.communications.models import (
    CommunicationChannel, CommunicationTemplate, CommunicationCampaign,
    Communication, CommunicationAttachment,
    # Messaging & Notification
    MessageThread, Message, MessageRecipient, Notification
)

User = get_user_model()

# ============================================================================
# HELPER SERIALIZERS
# ============================================================================

class SimpleUserSerializer(serializers.ModelSerializer):
    """Simple serializer for user details"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role']

# ============================================================================
# CONFIG SERIALIZERS
# ============================================================================

class CommunicationChannelSerializer(TenantAwareSerializer):
    class Meta:
        model = CommunicationChannel
        fields = '__all__'

class CommunicationTemplateSerializer(TenantAwareSerializer):
    channel_detail = RelatedFieldAlternative(
        source='channel',
        read_only=True,
        serializer=CommunicationChannelSerializer
    )
    approved_by_detail = RelatedFieldAlternative(
        source='approved_by',
        read_only=True,
        serializer=SimpleUserSerializer
    )
    
    # Computed
    available_variables = serializers.ListField(source='get_available_variables', read_only=True)

    class Meta:
        model = CommunicationTemplate
        fields = '__all__'
        read_only_fields = ['id', 'available_variables']

# ============================================================================
# CAMPAIGN SERIALIZERS
# ============================================================================

class CommunicationCampaignSerializer(TenantAwareSerializer):
    template_detail = RelatedFieldAlternative(
        source='template',
        read_only=True,
        serializer=CommunicationTemplateSerializer
    )
    
    # Computed
    delivery_rate = serializers.FloatField(read_only=True)
    open_rate = serializers.FloatField(read_only=True)
    click_rate = serializers.FloatField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = CommunicationCampaign
        fields = '__all__'
        read_only_fields = ['id', 'delivery_rate', 'open_rate', 'click_rate', 'is_active']

# ============================================================================
# COMMUNICATION SERIALIZERS
# ============================================================================

class CommunicationSerializer(TenantAwareSerializer):
    channel_detail = RelatedFieldAlternative(
        source='channel',
        read_only=True,
        serializer=CommunicationChannelSerializer
    )
    template_detail = RelatedFieldAlternative(
        source='template',
        read_only=True,
        serializer=CommunicationTemplateSerializer
    )
    campaign_detail = RelatedFieldAlternative(
        source='campaign',
        read_only=True,
        serializer=CommunicationCampaignSerializer
    )
    sender_detail = RelatedFieldAlternative(
        source='sender',
        read_only=True,
        serializer=SimpleUserSerializer
    )

    # Computed
    recipient_name = serializers.CharField(read_only=True)
    recipient_contact = serializers.CharField(read_only=True)
    is_scheduled = serializers.BooleanField(read_only=True)
    can_retry = serializers.BooleanField(read_only=True)

    class Meta:
        model = Communication
        fields = '__all__'
        read_only_fields = ['id', 'recipient_name', 'recipient_contact', 'is_scheduled', 'can_retry']

class CommunicationAttachmentSerializer(TenantAwareSerializer):
    communication_detail = RelatedFieldAlternative(
        source='communication',
        read_only=True,
        serializer=CommunicationSerializer
    )

# ============================================================================
# MESSAGING SERIALIZERS
# ============================================================================

class MessageRecipientSerializer(TenantAwareSerializer):
    recipient_detail = SimpleUserSerializer(source='recipient', read_only=True)
    
    class Meta:
        model = MessageRecipient
        fields = ['id', 'recipient', 'recipient_detail', 'is_read', 'read_at']

class MessageSerializer(TenantAwareSerializer):
    sender_detail = SimpleUserSerializer(source='sender', read_only=True)
    # attachments = MessageAttachmentSerializer(many=True, read_only=True) # Model does not exist yet
    
    class Meta:
        model = Message
        fields = ['id', 'thread', 'sender', 'sender_detail', 'body', 'message_type', 'subject', 'priority', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at', 'message_type']

class MessageThreadSerializer(TenantAwareSerializer):
    participants_detail = SimpleUserSerializer(source='participants', many=True, read_only=True)
    unread_count = serializers.IntegerField(read_only=True)
    last_message = serializers.SerializerMethodField()
    has_unread = serializers.SerializerMethodField()

    class Meta:
        model = MessageThread
        fields = ['id', 'title', 'created_by', 'participants', 'participants_detail', 'created_at', 'updated_at', 'last_message_at', 'is_active', 'unread_count', 'last_message', 'has_unread']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'last_message_at', 'unread_count']

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None
        
    def get_has_unread(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and hasattr(obj, 'unread_count'):
            return obj.unread_count > 0
        return False

# ============================================================================
# NOTIFICATION SERIALIZERS
# ============================================================================

class NotificationSerializer(TenantAwareSerializer):
    sender_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'title', 'message', 'notification_type', 'priority', 'is_read', 'read_at', 'action_url', 'created_at', 'sender_detail']
        read_only_fields = ['id', 'recipient', 'created_at', 'sender_detail']

    def get_sender_detail(self, obj):
        if hasattr(obj, 'sender') and obj.sender:
            return SimpleUserSerializer(obj.sender).data
        return None
