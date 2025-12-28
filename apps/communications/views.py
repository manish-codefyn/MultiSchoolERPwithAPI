import logging
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
from apps.core.views import (
    BaseView, BaseTemplateView, BaseListView, BaseDetailView, 
    BaseCreateView, BaseUpdateView, BaseDeleteView
)
from .models import (
    CommunicationChannel, CommunicationTemplate, 
    CommunicationCampaign, Communication, Notification
)
from .forms import (
    CommunicationChannelForm, CommunicationTemplateForm, 
    CommunicationCampaignForm, CommunicationComposeForm
)
from apps.core.utils.tenant import get_current_tenant

logger = logging.getLogger(__name__)

# ============================================================================
# DASHBOARD VIEW
# ============================================================================

class CommunicationDashboardView(BaseTemplateView):
    """
    Dashboard for all communications-related stats and quick actions
    """
    template_name = 'communications/dashboard.html'
    permission_required = 'communications.view_dashboard'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = self.tenant
        
        # Stats summary
        context['total_communications'] = Communication.objects.filter(tenant=tenant).count()
        context['total_sent'] = Communication.objects.filter(tenant=tenant, status='SENT').count()
        context['total_failed'] = Communication.objects.filter(tenant=tenant, status='FAILED').count()
        
        # Channel stats
        context['channels'] = CommunicationChannel.objects.filter(tenant=tenant).annotate(
            comm_count=Count('communications')
        )
        
        # Recent communications
        context['recent_comms'] = Communication.objects.filter(tenant=tenant).order_by('-created_at')[:5]
        
        # Active campaigns
        context['active_campaigns'] = CommunicationCampaign.objects.filter(
            tenant=tenant, status='RUNNING'
        ).count()
        
        # Unread notifications for current user
        if self.request.user.is_authenticated:
            context['unread_notifications'] = Notification.objects.filter(
                recipient=self.request.user, is_read=False
            ).count()
            
        return context

# ============================================================================
# CHANNEL VIEWS
# ============================================================================

class ChannelListView(BaseListView):
    model = CommunicationChannel
    template_name = 'communications/channel/list.html'
    context_object_name = 'channels'
    permission_required = 'communications.view_communicationchannel'
    search_fields = ['name', 'code', 'channel_type']

class ChannelCreateView(BaseCreateView):
    model = CommunicationChannel
    form_class = CommunicationChannelForm
    template_name = 'communications/channel/form.html'
    permission_required = 'communications.add_communicationchannel'
    success_url = reverse_lazy('communications:channel_list')

class ChannelUpdateView(BaseUpdateView):
    model = CommunicationChannel
    form_class = CommunicationChannelForm
    template_name = 'communications/channel/form.html'
    permission_required = 'communications.change_communicationchannel'
    success_url = reverse_lazy('communications:channel_list')

class ChannelDeleteView(BaseDeleteView):
    model = CommunicationChannel
    template_name = 'communications/common/confirm_delete.html'
    permission_required = 'communications.delete_communicationchannel'
    success_url = reverse_lazy('communications:channel_list')

# ============================================================================
# TEMPLATE VIEWS
# ============================================================================

class TemplateListView(BaseListView):
    model = CommunicationTemplate
    template_name = 'communications/template/list.html'
    context_object_name = 'templates'
    permission_required = 'communications.view_communicationtemplate'
    search_fields = ['name', 'code', 'subject']

class TemplateCreateView(BaseCreateView):
    model = CommunicationTemplate
    form_class = CommunicationTemplateForm
    template_name = 'communications/template/form.html'
    permission_required = 'communications.add_communicationtemplate'
    success_url = reverse_lazy('communications:template_list')

class TemplateUpdateView(BaseUpdateView):
    model = CommunicationTemplate
    form_class = CommunicationTemplateForm
    template_name = 'communications/template/form.html'
    permission_required = 'communications.change_communicationtemplate'
    success_url = reverse_lazy('communications:template_list')

class TemplateDeleteView(BaseDeleteView):
    model = CommunicationTemplate
    template_name = 'communications/common/confirm_delete.html'
    permission_required = 'communications.delete_communicationtemplate'
    success_url = reverse_lazy('communications:template_list')

# ============================================================================
# CAMPAIGN VIEWS
# ============================================================================

class CampaignListView(BaseListView):
    model = CommunicationCampaign
    template_name = 'communications/campaign/list.html'
    context_object_name = 'campaigns'
    permission_required = 'communications.view_communicationcampaign'
    search_fields = ['name', 'campaign_type']

class CampaignCreateView(BaseCreateView):
    model = CommunicationCampaign
    form_class = CommunicationCampaignForm
    template_name = 'communications/campaign/form.html'
    permission_required = 'communications.add_communicationcampaign'
    success_url = reverse_lazy('communications:campaign_list')

class CampaignUpdateView(BaseUpdateView):
    model = CommunicationCampaign
    form_class = CommunicationCampaignForm
    template_name = 'communications/campaign/form.html'
    permission_required = 'communications.change_communicationcampaign'
    success_url = reverse_lazy('communications:campaign_list')

class CampaignDeleteView(BaseDeleteView):
    model = CommunicationCampaign
    template_name = 'communications/common/confirm_delete.html'
    permission_required = 'communications.delete_communicationcampaign'
    success_url = reverse_lazy('communications:campaign_list')

# ============================================================================
# INDIVIDUAL COMMUNICATION VIEWS
# ============================================================================

class CommunicationListView(BaseListView):
    model = Communication
    template_name = 'communications/communication/list.html'
    context_object_name = 'communications'
    permission_required = 'communications.view_communication'
    search_fields = ['title', 'subject', 'external_recipient_name', 'external_recipient_email']
    paginate_by = 20

class CommunicationDetailView(BaseDetailView):
    model = Communication
    template_name = 'communications/communication/detail.html'
    context_object_name = 'communication'
    permission_required = 'communications.view_communication'

class CommunicationCreateView(BaseCreateView):
    """
    Compose a new communication
    """
    model = Communication
    form_class = CommunicationComposeForm
    template_name = 'communications/communication/form.html'
    permission_required = 'communications.add_communication'
    success_url = reverse_lazy('communications:communication_list')
    
    def form_valid(self, form):
        from django.contrib.contenttypes.models import ContentType
        from apps.students.models import Student
        from apps.users.models import User
        from apps.communications.models import Notification
        from django.utils import timezone
        import copy

        audience_type = form.cleaned_data.get('audience_type')
        send_notification = form.cleaned_data.get('send_notification')
        scheduled_for = form.cleaned_data.get('scheduled_for')
        
        # Determine status
        initial_status = 'SENT'
        if scheduled_for and scheduled_for > timezone.now():
            initial_status = 'SCHEDULED'

        # If SINGLE, fallback to default behavior (but add notification)
        if audience_type == 'SINGLE':
            form.instance.sender = self.request.user
            form.instance.status = initial_status
            if initial_status == 'SENT':
                form.instance.sent_at = timezone.now()
                
            response = super().form_valid(form)
            # Create notification if requested and is system recipient
            if send_notification and self.object.recipient:
                self._create_notification(self.object)
            return response
            
        # Bulk Logic
        recipients = self._get_bulk_recipients(form.cleaned_data)
        
        if not recipients:
            messages.warning(self.request, "No recipients found for the selected audience.")
            return self.form_invalid(form)
            
        # Create communications in bulk
        created_count = 0
        
        # Prepare base data
        base_comm_data = {
            'title': form.cleaned_data['title'],
            'subject': form.cleaned_data['subject'],
            'content': form.cleaned_data['content'],
            'channel': form.cleaned_data['channel'],
            'template': form.cleaned_data['template'],
            'priority': form.cleaned_data['priority'],
            'scheduled_for': scheduled_for,
            'status': initial_status,
            'direction': 'OUTBOUND',
            'sender': self.request.user,
            'tenant': self.tenant,
            'sent_at': timezone.now() if initial_status == 'SENT' else None
        }
        
        from apps.communications.models import Communication

        for recipient in recipients:
            # Create new instance
            comm = Communication(**base_comm_data)
            comm.recipient_type = ContentType.objects.get_for_model(recipient)
            comm.recipient_id = recipient.pk
            comm.save()
            
            # Create notification
            if send_notification:
                # Resolve User object for notification
                user_recipient = None
                if isinstance(recipient, User):
                    user_recipient = recipient
                elif hasattr(recipient, 'user'):
                    user_recipient = recipient.user
                
                if user_recipient:
                    self._create_notification(comm, user_recipient)
            
            created_count += 1

        messages.success(self.request, f"Successfully queued {created_count} communications.")
        return redirect(self.success_url)

    def _get_bulk_recipients(self, data):
        from apps.students.models import Student
        from apps.users.models import User
        
        audience_type = data.get('audience_type')
        target_class = data.get('target_class')
        
        if audience_type == 'ALL_STUDENTS':
            return Student.objects.filter(tenant=self.tenant, is_active=True)
            
        elif audience_type == 'CLASS':
            if target_class:
                return Student.objects.filter(
                     tenant=self.tenant, 
                     is_active=True,
                     current_class=target_class # Assuming relationship name, check models if needed
                )
        
        elif audience_type == 'ALL_PARENTS':
            # Logic to get parents from students
            return [] # Placeholder, complex logic needed for parents
            
        elif audience_type == 'ALL_TEACHERS':
            return User.objects.filter(
                tenant=self.tenant, 
                is_active=True,
                role__name='TEACHER' # Adjust based on Role model
            )
            
        elif audience_type == 'ALL_STAFF':
            # Exclude students/parents if possible, or filter by role is_staff
            return User.objects.filter(tenant=self.tenant, is_active=True, is_staff=True)
            
        return []

    def _create_notification(self, communication, user_recipient=None):
        from apps.communications.models import Notification
        from django.contrib.contenttypes.models import ContentType
        
        recipient = user_recipient if user_recipient else communication.recipient
        
        # Ensure recipient is a User
        if not recipient or not hasattr(recipient, 'pk'): # Basic check
             return

        # If recipient is not a User model (e.g. Student), try to get .user
        if hasattr(recipient, 'user') and recipient.user:
            recipient = recipient.user
            
        if not recipient._meta.model_name == 'user':
            return # Cannot notify non-users directly via System Notification model usually

        # Get absolute URL or empty string (URLField checks for valid URL scheme)
        url = ""
        if hasattr(communication, 'get_absolute_url'):
            try:
                # build_absolute_uri ensures http://domain... which URLField requires
                url = self.request.build_absolute_uri(communication.get_absolute_url())
            except Exception:
                pass

        Notification.objects.create(
            tenant=self.tenant,
            recipient=recipient,
            title=f"New Message: {communication.title}",
            message=communication.content[:200], # Truncate
            notification_type="MESSAGE",
            priority=communication.priority,
            content_type=ContentType.objects.get_for_model(communication),
            object_id=communication.id,
            action_url=url
        )

class RecipientLookupView(BaseView):
    """
    API view to lookup recipients based on content type
    """
    def get(self, request, *args, **kwargs):
        from django.http import JsonResponse
        from django.contrib.contenttypes.models import ContentType
        
        content_type_id = request.GET.get('content_type_id')
        query = request.GET.get('q', '')
        
        if not content_type_id:
            return JsonResponse({'results': []})
            
        try:
            content_type = ContentType.objects.get(id=content_type_id)
            model_class = content_type.model_class()
            
            # Base queryset
            queryset = model_class.objects.all()
            
            # Apply tenant filtering if model is tenant-aware
            if hasattr(model_class, 'tenant'):
                queryset = queryset.filter(tenant=self.tenant)
                
            # Filter by query
            if query:
                # Adjust search fields based on model
                if hasattr(model_class, 'first_name'):
                    queryset = queryset.filter(
                        Q(first_name__icontains=query) | 
                        Q(last_name__icontains=query)
                    )
                elif hasattr(model_class, 'name'):
                    queryset = queryset.filter(name__icontains=query)
                elif hasattr(model_class, 'username'):
                    queryset = queryset.filter(username__icontains=query)
            
            results = []
            for obj in queryset[:50]:  # Limit results
                text = str(obj)
                if hasattr(obj, 'get_full_name'):
                    text = obj.get_full_name()
                elif hasattr(obj, 'get_display_name'):
                    text = obj.get_display_name()
                    
                # For Students, append admission number
                if hasattr(obj, 'admission_number'):
                    text = f"{text} ({obj.admission_number})"
                    
                results.append({
                    'id': str(obj.pk) if hasattr(obj, 'pk') else str(obj.id),
                    'text': text
                })
                
            return JsonResponse({'results': results})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

from django.views import View
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import (
    MessageThread, Message, CommunicationPreference, SystemMessage,
    MessageThread, Message, CommunicationPreference, SystemMessage,
    MessageRecipient, Notification
)
from django.contrib.contenttypes.models import ContentType
from .forms import (
    MessageThreadForm, MessageForm, CommunicationPreferenceForm
)

# ============================================================================
# NOTIFICATION VIEWS
# ============================================================================

class NotificationListView(BaseListView):
    """
    List user's notifications
    """
    model = Notification
    template_name = 'communications/notification/list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('content_type').order_by('-created_at')

class NotificationDetailView(BaseDetailView):
    """
    View notification details and mark as read
    """
    model = Notification
    template_name = 'communications/notification/detail.html'
    context_object_name = 'notification'

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_read:
            obj.mark_as_read()
        return obj

class NotificationDeleteView(BaseDeleteView):
    """
    Dismiss (delete) a notification
    """
    model = Notification
    template_name = 'communications/common/confirm_delete.html'
    success_url = reverse_lazy('communications:notification_list')

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

class MarkNotificationReadView(LoginRequiredMixin, View):
    """
    AJAX view to mark notification as read
    """
    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, recipient=request.user)
            notification.mark_as_read()
            return JsonResponse({'status': 'success'})
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)

class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    """
    AJAX view to mark all notifications as read
    """
    def post(self, request):
        Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True, read_at=timezone.now())
        return JsonResponse({'status': 'success'})

# ============================================================================
# MESSAGING (INTERNAL CHAT) VIEWS
# ============================================================================

class MessageThreadListView(BaseListView):
    """
    Inbox / List of conversations
    """
    model = MessageThread
    template_name = 'communications/thread/app_chat.html'
    context_object_name = 'threads'
    paginate_by = 15

    def get_queryset(self):
        return MessageThread.objects.filter(
            participants=self.request.user,
            is_active=True
        ).prefetch_related('participants').order_by('-last_message_at')

class MessageThreadCreateView(BaseCreateView):
    """
    Start a new conversation
    """
    model = MessageThread
    form_class = MessageThreadForm
    template_name = 'communications/thread/form.html'
    success_url = reverse_lazy('communications:thread_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Add creator to participants
        self.object.participants.add(self.request.user)
        
        # Initial message
        initial_message = form.cleaned_data.get('initial_message')
        participants = form.cleaned_data.get('participants')
        
        print(f"DEBUG: Thread created. Participants from form: {participants}")
        
        if initial_message:
            msg = Message.objects.create(
                sender=self.request.user,
                body=initial_message,
                message_type='MESSAGE',
                thread=self.object,
                subject=self.object.title[:200]
            )
            
            # Combine creator and form participants
            all_participants = list(participants) if participants else []
            # We already added request.user to M2M, but let's be safe for notification loop
            
            print(f"DEBUG: Sending to participants: {all_participants}")

            for participant in all_participants:
                if participant != self.request.user:
                    print(f"DEBUG: Creating recipient/notification for {participant}")
                    
                    # 1. Create Recipient Record (Read/Unread status)
                    MessageRecipient.objects.create(
                        message=msg, 
                        recipient=participant
                    )
                    
                    action_url = self.request.build_absolute_uri(reverse('communications:thread_detail', kwargs={'pk': self.object.id}))
                    
                    # 2. Create Persistent Notification (For bell icon)
                    Notification.objects.create(
                        tenant=self.request.tenant,
                        recipient=participant,
                        title=f"New Conversation: {self.object.title[:30]}...",
                        message=f"You have been added to a new conversation by {self.request.user.get_full_name()}",
                        notification_type="MESSAGE",
                        priority="MEDIUM", # Was NORMAL (Invalid)
                        content_type=ContentType.objects.get_for_model(self.object),
                        object_id=self.object.id,
                        action_url=action_url
                    )
        
        return response

class MessageThreadDetailView(BaseDetailView):
    """
    View conversation and reply
    """
    model = MessageThread
    template_name = 'communications/thread/app_chat.html'
    context_object_name = 'thread'

    def get_queryset(self):
        return MessageThread.objects.filter(participants=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MessageForm()
        # Fetch threads for sidebar
        context['threads'] = MessageThread.objects.filter(
            participants=self.request.user,
            is_active=True
        ).prefetch_related('participants').order_by('-last_message_at')
        return context

class MessageCreateView(BaseCreateView):
    """
    Post a reply to a thread
    """
    model = Message
    form_class = MessageForm
    
    def form_valid(self, form):
        thread_id = self.kwargs.get('pk')
        try:
            thread = MessageThread.objects.get(pk=thread_id, participants=self.request.user)
        except MessageThread.DoesNotExist:
            return redirect('communications:thread_list') # Handle better
        
        message = form.save(commit=False)
        message.sender = self.request.user
        message.thread = thread
        message.subject = f"Re: {thread.title}"[:200]
        message.save()
        
        # Create recipients
        for participant in thread.participants.all():
            if participant != self.request.user:
                MessageRecipient.objects.create(
                    message=message,
                    recipient=participant
                )
                action_url = self.request.build_absolute_uri(reverse('communications:thread_detail', kwargs={'pk': thread.id}))

                # Create persistent notification for reply
                Notification.objects.create(
                    tenant=self.request.tenant,
                    recipient=participant,
                    title=f"New Message in {thread.title[:30]}...",
                    message=f"{self.request.user.get_full_name()} sent a message: {message.body[:50]}...",
                    notification_type="MESSAGE",
                    priority="MEDIUM", # Was NORMAL (Invalid)
                    content_type=ContentType.objects.get_for_model(thread),
                    object_id=thread.id,
                    action_url=action_url
                )
        
        # Update thread
        thread.last_message_at = timezone.now()
        thread.save()
        
        return redirect('communications:thread_detail', pk=thread.pk)

# ============================================================================
# PREFERENCE VIEWS
# ============================================================================

class CommunicationPreferenceUpdateView(BaseUpdateView):
    """
    Update user communication preferences
    """
    model = CommunicationPreference
    form_class = CommunicationPreferenceForm
    template_name = 'communications/preference/form.html'
    success_url = reverse_lazy('communications:preference_update')

    def get_object(self, queryset=None):
        # Get or create preferences for current user
        obj, created = CommunicationPreference.objects.get_or_create(user=self.request.user)
        return obj
    
    def form_valid(self, form):
        messages.success(self.request, "Preferences updated successfully.")
        return super().form_valid(form)

# ============================================================================
# COMMUNICATION FIXES
# ============================================================================

class CommunicationUpdateView(BaseUpdateView):
    model = Communication
    form_class = CommunicationComposeForm
    template_name = 'communications/communication/form.html'
    permission_required = 'communications.change_communication'
    success_url = reverse_lazy('communications:communication_list')

class CommunicationDeleteView(BaseDeleteView):
    model = Communication
    template_name = 'communications/common/confirm_delete.html'
    permission_required = 'communications.delete_communication'
    success_url = reverse_lazy('communications:communication_list')

