from django.urls import path
from apps.communications.api.views import (
    CommunicationChannelListCreateAPIView, CommunicationChannelDetailAPIView,
    CommunicationTemplateListCreateAPIView, CommunicationTemplateDetailAPIView,
    CommunicationCampaignListCreateAPIView, CommunicationCampaignDetailAPIView,
    CommunicationListCreateAPIView, CommunicationDetailAPIView,
    CommunicationAttachmentListCreateAPIView, CommunicationAttachmentDetailAPIView,
    # Messaging & Notification
    MessageThreadListCreateAPIView, MessageThreadDetailAPIView,
    MessageListCreateAPIView,
    NotificationListAPIView, NotificationDetailAPIView, MarkAllNotificationsReadAPIView
)
from .dashboard_view import CommunicationsDashboardAPIView

urlpatterns = [
    # Dashboard
    path('dashboard/', CommunicationsDashboardAPIView.as_view(), name='dashboard'),

    # Channels
    path('channels/', CommunicationChannelListCreateAPIView.as_view(), name='communicationchannel-list'),
    path('channels/<uuid:pk>/', CommunicationChannelDetailAPIView.as_view(), name='communicationchannel-detail'),

    # Templates
    path('templates/', CommunicationTemplateListCreateAPIView.as_view(), name='communicationtemplate-list'),
    path('templates/<uuid:pk>/', CommunicationTemplateDetailAPIView.as_view(), name='communicationtemplate-detail'),

    # Campaigns
    path('campaigns/', CommunicationCampaignListCreateAPIView.as_view(), name='communicationcampaign-list'),
    path('campaigns/<uuid:pk>/', CommunicationCampaignDetailAPIView.as_view(), name='communicationcampaign-detail'),

    # Communications
    path('', CommunicationListCreateAPIView.as_view(), name='communication-list'),
    path('<uuid:pk>/', CommunicationDetailAPIView.as_view(), name='communication-detail'),

    # Attachments
    path('attachments/', CommunicationAttachmentListCreateAPIView.as_view(), name='communicationattachment-list'),
    path('attachments/<uuid:pk>/', CommunicationAttachmentDetailAPIView.as_view(), name='communicationattachment-detail'),

    # ==========================
    # MESSAGING (CHAT)
    # ==========================
    path('threads/', MessageThreadListCreateAPIView.as_view(), name='api_thread_list'),
    path('threads/<uuid:pk>/', MessageThreadDetailAPIView.as_view(), name='api_thread_detail'),
    path('threads/<uuid:pk>/messages/', MessageListCreateAPIView.as_view(), name='api_thread_messages'),

    # ==========================
    # NOTIFICATIONS
    # ==========================
    path('notifications/', NotificationListAPIView.as_view(), name='api_notification_list'),
    path('notifications/mark-all-read/', MarkAllNotificationsReadAPIView.as_view(), name='api_notification_mark_all_read'),
    path('notifications/<uuid:pk>/', NotificationDetailAPIView.as_view(), name='api_notification_detail'),
]
