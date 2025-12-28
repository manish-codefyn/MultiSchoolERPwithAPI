from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.CommunicationDashboardView.as_view(), name='dashboard'),
    
    # Channels
    path('channels/', views.ChannelListView.as_view(), name='channel_list'),
    path('channels/create/', views.ChannelCreateView.as_view(), name='channel_create'),
    path('channels/<uuid:pk>/update/', views.ChannelUpdateView.as_view(), name='channel_update'),
    path('channels/<uuid:pk>/delete/', views.ChannelDeleteView.as_view(), name='channel_delete'),
    
    # Templates
    path('templates/', views.TemplateListView.as_view(), name='template_list'),
    path('templates/create/', views.TemplateCreateView.as_view(), name='template_create'),
    path('templates/<uuid:pk>/update/', views.TemplateUpdateView.as_view(), name='template_update'),
    path('templates/<uuid:pk>/delete/', views.TemplateDeleteView.as_view(), name='template_delete'),
    
    # Campaigns
    path('campaigns/', views.CampaignListView.as_view(), name='campaign_list'),
    path('campaigns/create/', views.CampaignCreateView.as_view(), name='campaign_create'),
    path('campaigns/<uuid:pk>/update/', views.CampaignUpdateView.as_view(), name='campaign_update'),
    path('campaigns/<uuid:pk>/delete/', views.CampaignDeleteView.as_view(), name='campaign_delete'),
    
    # Individual Communications (Admin/Bulk)
    path('messages/', views.CommunicationListView.as_view(), name='communication_list'),
    path('messages/compose/', views.CommunicationCreateView.as_view(), name='communication_create'),
    path('messages/<uuid:pk>/', views.CommunicationDetailView.as_view(), name='communication_detail'),
    path('messages/<uuid:pk>/update/', views.CommunicationUpdateView.as_view(), name='communication_update'),
    path('messages/<uuid:pk>/delete/', views.CommunicationDeleteView.as_view(), name='communication_delete'), # Fixed view reference
    
    # Notifications (In-App)
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<uuid:pk>/', views.NotificationDetailView.as_view(), name='notification_detail'),
    path('notifications/<uuid:pk>/delete/', views.NotificationDeleteView.as_view(), name='notification_delete'),
    path('notifications/<uuid:pk>/mark-read/', views.MarkNotificationReadView.as_view(), name='notification_mark_read'),
    path('notifications/mark-all-read/', views.MarkAllNotificationsReadView.as_view(), name='notification_mark_all_read'),

    # Internal Messaging (Chat)
    path('inbox/', views.MessageThreadListView.as_view(), name='thread_list'),
    path('inbox/new/', views.MessageThreadCreateView.as_view(), name='thread_create'),
    path('inbox/<uuid:pk>/', views.MessageThreadDetailView.as_view(), name='thread_detail'),
    path('inbox/<uuid:pk>/reply/', views.MessageCreateView.as_view(), name='thread_reply'),

    # Preferences
    path('preferences/', views.CommunicationPreferenceUpdateView.as_view(), name='preference_update'),

    # API
    path('api/recipient-lookup/', views.RecipientLookupView.as_view(), name='recipient_lookup'), 
]
