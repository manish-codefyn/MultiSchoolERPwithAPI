
from django import forms
from django.utils.translation import gettext_lazy as _
from apps.core.forms import TenantAwareModelForm
from .models import (
    CommunicationChannel, CommunicationTemplate, 
    CommunicationCampaign, Communication, CommunicationAttachment,
    MessageThread, Message, CommunicationPreference
)

class CommunicationChannelForm(TenantAwareModelForm):
    """Form for creating and updating communication channels"""
    class Meta:
        model = CommunicationChannel
        fields = [
            'name', 'code', 'channel_type', 'description', 
            'is_active', 'priority', 'rate_limit', 'cost_per_message'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'config': forms.Textarea(attrs={'rows': 5}),
        }

class CommunicationTemplateForm(TenantAwareModelForm):
    """Form for creating and updating communication templates"""
    class Meta:
        model = CommunicationTemplate
        fields = [
            'name', 'code', 'template_type', 'channel', 
            'subject', 'body', 'language', 'description', 
            'variables', 'is_active', 'requires_approval'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'body': forms.Textarea(attrs={'rows': 10}),
            'variables': forms.Textarea(attrs={'rows': 3, 'placeholder': '["variable1", "variable2"]'}),
        }

class CommunicationCampaignForm(TenantAwareModelForm):
    """Form for creating and updating communication campaigns"""
    class Meta:
        model = CommunicationCampaign
        fields = [
            'name', 'campaign_type', 'template', 'scheduled_for', 
            'is_recurring', 'recurrence_pattern', 'target_audience', 
            'budget', 'rate_limit'
        ]
        widgets = {
            'scheduled_for': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'recurrence_pattern': forms.Textarea(attrs={'rows': 3}),
            'target_audience': forms.Textarea(attrs={'rows': 5}),
        }

class CommunicationComposeForm(TenantAwareModelForm):
    """Form for composing individual communications"""
    AUDIENCE_CHOICES = (
        ('SINGLE', _('Single Recipient')),
        ('ALL_STUDENTS', _('All Students')),
        ('ALL_PARENTS', _('All Parents')),
        ('ALL_STAFF', _('All Staff')),
        ('ALL_TEACHERS', _('All Teachers')),
        ('CLASS', _('Specific Class')),
    )

    audience_type = forms.ChoiceField(
        choices=AUDIENCE_CHOICES,
        initial='SINGLE',
        widget=forms.RadioSelect(attrs={'class': 'btn-check'}),
        label=_("Audience Target")
    )
    
    target_class = forms.ModelChoiceField(
        queryset=CommunicationChannel.objects.none(),
        required=False,
        label=_("Target Class"),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    send_notification = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Send System Notification"),
        help_text=_("Also send an in-app system notification")
    )

    class Meta:
        model = Communication
        fields = [
            'audience_type', 'target_class',
            'title', 'subject', 'content', 'channel', 
            'template', 'recipient_type', 'recipient_id',
            'external_recipient_name', 'external_recipient_email', 
            'external_recipient_phone', 'priority', 'scheduled_for',
            'send_notification'
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'scheduled_for': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'recipient_id': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.contenttypes.models import ContentType
        from apps.academics.models import SchoolClass
        
        # Filter channels and templates to tenant
        self.fields['channel'].queryset = CommunicationChannel.objects.filter(
            tenant=self.tenant, is_active=True
        )
        self.fields['template'].queryset = CommunicationTemplate.objects.filter(
            tenant=self.tenant, is_active=True
        )
        self.fields['template'].required = False
        
        # Target Class Options
        self.fields['target_class'].queryset = SchoolClass.objects.filter(
            tenant=self.tenant, is_active=True
        )

        # Filter recipient types to relevant models only
        relevant_models = ['user', 'student', 'staff', 'parent']
        self.fields['recipient_type'].queryset = ContentType.objects.filter(
            model__in=relevant_models
        )
        self.fields['recipient_type'].required = False
        self.fields['recipient_id'].required = False

    def clean(self):
        cleaned_data = super().clean()
        audience_type = cleaned_data.get('audience_type')
        recipient_type = cleaned_data.get('recipient_type')
        recipient_id = cleaned_data.get('recipient_id')
        ext_name = cleaned_data.get('external_recipient_name')
        ext_email = cleaned_data.get('external_recipient_email')
        ext_phone = cleaned_data.get('external_recipient_phone')
        target_class = cleaned_data.get('target_class')

        if audience_type == 'SINGLE':
            # Logic to check if either system recipient or external contact is present
            system_recipient = recipient_type and recipient_id
            external_contact = ext_name and (ext_email or ext_phone)

            if not (system_recipient or external_contact):
                raise forms.ValidationError(
                    _("For Single Recipient, either system recipient or external contact information is required")
                )
            
            if recipient_type and not recipient_id:
                self.add_error('recipient_id', _("Recipient ID is required when Recipient Type is selected"))
        
        elif audience_type == 'CLASS' and not target_class:
            self.add_error('target_class', _("Class must be selected for Class-wise communication"))
            
        return cleaned_data

    def _post_clean(self):
        super()._post_clean()
        # If audience is bulk, ignore the model's recipient validation error
        if self.cleaned_data.get('audience_type') != 'SINGLE':
            if 'recipient_id' in self._errors:
                del self._errors['recipient_id']
                if not self._errors:
                    # If removing this made the form valid, clear the cleaned_data cache logic or validation flags if needed
                    # Django ModelForm checks is_valid() based on bool(self.errors)
                    pass

class MessageThreadForm(TenantAwareModelForm):
    """Form for creating new conversation threads"""
    
    # Allow selecting multiple users to start a conversation with
    participants = forms.ModelMultipleChoiceField(
        queryset=CommunicationChannel.objects.none(), # Dummy QS, will be overridden in __init__
        widget=forms.SelectMultiple(attrs={'class': 'form-select select2'}),
        required=True,
        label=_("Participants")
    )
    
    initial_message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': _("Type your first message...")}),
        required=True,
        label=_("Message")
    )

    class Meta:
        model = MessageThread
        fields = ['title', 'thread_type', 'is_private']
        widgets = {
            'thread_type': forms.Select(attrs={'class': 'form-select'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.users.models import User
        # Filter participants to active users in current tenant (exclude self)
        # We must set the queryset here again to the correct model
        self.fields['participants'].queryset = User.objects.filter(
            tenant=self.tenant, is_active=True
        ).exclude(id=self.user.id)

class MessageForm(TenantAwareModelForm):
    """Form for replying to a thread (sending a message)"""
    class Meta:
        model = Message
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'placeholder': _('Type your reply here...')
            }),
        }

class CommunicationPreferenceForm(TenantAwareModelForm):
    """Form for updating user communication preferences"""
    class Meta:
        model = CommunicationPreference
        fields = [
            'email_enabled', 'sms_enabled', 'push_enabled', 'in_app_enabled',
            'daily_digest', 'weekly_digest', 'digest_time',
            'academic_notifications', 'financial_notifications', 
            'event_notifications', 'security_notifications'
        ]
        widgets = {
            'digest_time': forms.TimeInput(attrs={'type': 'time'}),
        }
