from django.db import models
from django.utils.text import slugify
from django_cryptography.fields import encrypt
from django_tenants.models import TenantMixin, DomainMixin
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from apps.core.models import UUIDModel, TimeStampedModel, BaseModel, BaseSharedModel

class Tenant(TenantMixin, BaseSharedModel):
    """
    Secure multi-tenant implementation with enterprise features
    """
    name = models.CharField(
        max_length=255,
        verbose_name='Organization Name',
        help_text='Legal name of the institution/organization'
    )
    display_name = models.CharField(
        max_length=255,
        verbose_name='Display Name',
        help_text='Public-facing name for the institution'
    )
    slug = models.SlugField(max_length=150, unique=True, blank=True)

    # Tenant Status & Configuration
    STATUS_ACTIVE = 'active'
    STATUS_SUSPENDED = 'suspended'
    STATUS_TRIAL = 'trial'
    STATUS_EXPIRED = 'expired'
    
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_SUSPENDED, 'Suspended'),
        (STATUS_TRIAL, 'Trial'),
        (STATUS_EXPIRED, 'Expired'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_TRIAL,
        db_index=True,
        verbose_name='Tenant Status'
    )

    # Onboarding Status
    ONBOARDING_PENDING = 'PENDING'
    ONBOARDING_PROVISIONING = 'PROVISIONING'
    ONBOARDING_READY = 'READY'
    ONBOARDING_FAILED = 'FAILED'

    ONBOARDING_STATUS_CHOICES = [
        (ONBOARDING_PENDING, 'Pending'),
        (ONBOARDING_PROVISIONING, 'Provisioning'),
        (ONBOARDING_READY, 'Ready'),
        (ONBOARDING_FAILED, 'Failed'),
    ]

    onboarding_status = models.CharField(
        max_length=20,
        choices=ONBOARDING_STATUS_CHOICES,
        default=ONBOARDING_PENDING,
        verbose_name='Onboarding Status'
    )
    
    # Subscription & Limits
    PLAN_BASIC = 'basic'
    PLAN_PROFESSIONAL = 'professional'
    PLAN_ENTERPRISE = 'enterprise'
    
    PLAN_CHOICES = [
        (PLAN_BASIC, 'Basic'),
        (PLAN_PROFESSIONAL, 'Professional'),
        (PLAN_ENTERPRISE, 'Enterprise'),
    ]
    
    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default=PLAN_BASIC,
        verbose_name='Subscription Plan'
    )
    
    max_users = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(1), MaxValueValidator(10000)],
        verbose_name='Maximum Users',
        help_text='Maximum number of active users allowed'
    )
    
    max_storage_mb = models.PositiveIntegerField(
        default=1024,  # 1GB
        verbose_name='Storage Limit (MB)',
        help_text='Maximum storage space in megabytes'
    )
    
    # Contact Information
    contact_email = models.EmailField(
        verbose_name='Contact Email',
        help_text='Primary contact email for administrative communications'
    )
    
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Contact Phone',
        help_text='Primary contact phone number'
    )


    
    # Security & Compliance
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name='Active Status',
        help_text='Designates whether this tenant can access the system'
    )
    
    force_password_reset = models.BooleanField(
        default=False,
        verbose_name='Force Password Reset',
        help_text='Require all users to reset their passwords on next login'
    )
    
    mfa_required = models.BooleanField(
        default=False,
        verbose_name='MFA Required',
        help_text='Require multi-factor authentication for all users'
    )
    
    password_policy = models.JSONField(
        default=dict,
        verbose_name='Password Policy',
        help_text='Custom password policy configuration'
    )
    
    # Subscription Management
    trial_ends_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Trial End Date'
    )
    
    subscription_ends_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Subscription End Date'
    )
    
    # Auto-create schema for new tenants
    auto_create_schema = True

    class Meta:
        db_table = 'tenants'
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'
        indexes = [
            models.Index(fields=['schema_name']),
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['plan', 'status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.schema_name})"

    @property
    def has_api_access(self):
        """Check if tenant has API access enabled"""
        return self.status == self.STATUS_ACTIVE and self.is_active

    def get_api_usage_today(self):
        """Get today's API usage"""
        from django.utils import timezone
        from datetime import date
        
        return APIUsageLog.objects.filter(
            tenant=self,
            created_at__date=timezone.now().date()
        ).aggregate(total=models.Sum('request_count'))['total'] or 0

    def can_make_api_request(self):
        """Check if tenant can make API request"""
        if not self.has_api_access:
            return False
        
        usage_today = self.get_api_usage_today()
        return usage_today < self.max_api_requests_per_day

    @property
    def branding_info(self):
        """Get complete branding information"""
        if hasattr(self, 'configuration'):
            config = self.configuration
            return {
                'name': self.name,
                'logo': config.logo.url if config.logo else '/static/images/logo.png',
                'primary_color': config.primary_color,
                'secondary_color': config.secondary_color,
                'mfa_required': self.mfa_required,
            }
        return {
            'name': self.name,
            'logo': '/static/images/logo.png',
            'primary_color': '#3B82F6',  # Default from TenantConfiguration
            'secondary_color': '#1E40AF',  # Default from TenantConfiguration
            'mfa_required': self.mfa_required,
        }
        
    def audit_log(self, action, user=None, metadata=None, severity='MEDIUM'):
        """Create security audit log entry"""
        from apps.auth.models import SecurityEvent  # Adjust import path
        
        SecurityEvent.objects.create(
            tenant=self,
            user=user,
            event_type=action,
            severity=severity,
            description=f"Tenant {self.name}: {action}",
            metadata=metadata or {}
        )

    def clean(self):
        """
        Comprehensive tenant validation
        """
        from django.core.exceptions import ValidationError
        
        super().clean()
        
        # Validate schema name format
        if self.schema_name:
            if not self.schema_name.replace('_', '').isalnum():
                raise ValidationError({
                    'schema_name': 'Schema name can only contain alphanumeric characters and underscores.'
                })
            if len(self.schema_name) > 63:
                raise ValidationError({
                    'schema_name': 'Schema name cannot exceed 63 characters.'
                })

    @property
    def is_trial(self):
        """Check if tenant is in trial period"""
        from django.utils import timezone
        return (self.status == self.STATUS_TRIAL and 
                self.trial_ends_at and 
                self.trial_ends_at > timezone.now())

    @property
    def is_subscription_active(self):
        """Check if subscription is active"""
        from django.utils import timezone
        return (self.status == self.STATUS_ACTIVE and
                (not self.subscription_ends_at or 
                 self.subscription_ends_at > timezone.now()))

    def get_user_count(self):
        """Get current active user count"""
        from apps.users.models import User
        return User.objects.filter(tenant=self, is_active=True).count()

    def can_add_user(self):
        """Check if tenant can add more users"""
        return self.get_user_count() < self.max_users

    def suspend(self, reason="Administrative action"):
        """Suspend tenant access"""
        self.status = self.STATUS_SUSPENDED
        self.is_active = False
        self.save(update_fields=['status', 'is_active'])
        
        # Log suspension
        self.audit_log('TENANT_SUSPENDED', None, {'reason': reason}, 'HIGH')

    def activate(self):
        """Activate tenant"""
        self.status = self.STATUS_ACTIVE
        self.is_active = True
        self.save(update_fields=['status', 'is_active'])
        
        # Log activation
        self.audit_log('TENANT_ACTIVATED', None, {}, 'MEDIUM')

    def validate_tenant_limits(self):
        """Validate tenant against plan limits"""
        errors = {}
        
        user_count = self.get_user_count()
        if user_count > self.max_users:
            errors['max_users'] = f'User limit exceeded: {user_count}/{self.max_users}'
            
        # Add storage validation when storage tracking is implemented
        return errors

    def save(self, *args, **kwargs):
        """Override save to handle slug, validation, and auto-schema creation."""
        
        # Auto-generate slug if missing
        if not getattr(self, "slug", None) or self.slug == '':
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        
        # Run model validation
        self.clean()

        # Check if new tenant
        is_new = self._state.adding

        # Save tenant first
        super().save(*args, **kwargs)

        # After save: auto create schema & configuration
        if is_new and getattr(self, "auto_create_schema", False):
            from django_tenants.utils import schema_context
            from apps.auth.models import RolePermission

            # Create schema
            self.create_schema(check_if_exists=True)

            # Create per-tenant default configuration & permissions
            with schema_context(self.schema_name):
                TenantConfiguration.objects.create(tenant=self)
                PaymentConfiguration.objects.create(tenant=self)
                AnalyticsConfiguration.objects.create(tenant=self)
                RolePermission.create_default_permissions(tenant=self)


class Domain(DomainMixin, BaseModel):
    """
    Custom domain model with enhanced security features
    """
    is_primary = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='Primary Domain',
        help_text='Designates the primary domain for this tenant'
    )
    
    ssl_enabled = models.BooleanField(
        default=True,
        verbose_name='SSL Enabled',
        help_text='Enable SSL for this domain'
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Domain Verified',
        help_text='Domain ownership has been verified'
    )
    
    verification_token = models.CharField(
        max_length=64,
        blank=True,
        editable=False,
        verbose_name='Domain Verification Token'
    )

    class Meta:
        db_table = 'tenant_domains'
        verbose_name = 'Domain'
        verbose_name_plural = 'Domains'
        indexes = [
            models.Index(fields=['domain', 'is_primary']),
            models.Index(fields=['tenant', 'is_primary']),
        ]

    def clean(self):
        """
        Domain validation
        """
        from django.core.exceptions import ValidationError
        
        super().clean()
        
        # Ensure only one primary domain per tenant
        if self.is_primary:
            existing_primary = Domain.objects.filter(
                tenant=self.tenant, 
                is_primary=True
            ).exclude(id=self.id)
            
            if existing_primary.exists():
                raise ValidationError({
                    'is_primary': 'Only one domain can be set as primary per tenant.'
                })

    def generate_verification_token(self):
        """Generate domain verification token"""
        import secrets
        self.verification_token = secrets.token_urlsafe(32)
        self.save(update_fields=['verification_token'])
        return self.verification_token

    def verify_domain(self, token):
        """Verify domain ownership"""
        if self.verification_token == token:
            self.is_verified = True
            self.verification_token = ''  # Clear token after verification
            self.save(update_fields=['is_verified', 'verification_token'])
            return True
        return False

    def save(self, *args, **kwargs):
        """Ensure only one primary domain per tenant"""
        if self.is_primary:
            # Remove primary status from other domains
            Domain.objects.filter(
                tenant=self.tenant, 
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        
        super().save(*args, **kwargs)
    
    @property
    def verification_url(self):
        """Generate domain verification URL"""
        if self.verification_token:
            return f"https://{self.domain}/verify-domain/{self.verification_token}/"
        return None

    @property
    def logo(self):
        """Get tenant logo from configuration"""
        if hasattr(self, 'configuration') and self.configuration.logo:
            return self.configuration.logo
        return None
    
    @property
    def branding(self):
        """Get complete branding information"""
        if hasattr(self, 'configuration'):
            return {
                'logo': self.configuration.logo,
                'primary_color': self.configuration.primary_color,
                'secondary_color': self.configuration.secondary_color,
            }
        return None

class TenantConfiguration(UUIDModel, TimeStampedModel):
    """
    Tenant-specific configuration and settings
    """
    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name='configuration',
        verbose_name='Tenant'
    )
    
    # Academic Configuration
    affiliation_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Affiliation Number',
        help_text='Board affiliation number (e.g., CBSE/state board)'
    )
    
    school_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='School Code',
        help_text='Official school code'
    )

    academic_year = models.CharField(
        max_length=20,
        default='2024-2025',
        verbose_name='Current Academic Year'
    )
    
    # Localization
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        verbose_name='Default Timezone'
    )
    
    language = models.CharField(
        max_length=10,
        default='en',
        verbose_name='Default Language'
    )
    
    currency = models.CharField(
        max_length=3,
        default='INR',
        verbose_name='Default Currency'
    )
    
    date_format = models.CharField(
        max_length=20,
        default='YYYY-MM-DD',
        verbose_name='Date Format'
    )
    
    # Security Settings
    session_timeout = models.PositiveIntegerField(
        default=30,
        verbose_name='Session Timeout (minutes)'
    )
    
    max_login_attempts = models.PositiveIntegerField(
        default=5,
        verbose_name='Maximum Login Attempts'
    )
    
    password_expiry_days = models.PositiveIntegerField(
        default=90,
        verbose_name='Password Expiry (days)'
    )
    
    # Feature Flags
    enable_library = models.BooleanField(
        default=True,
        verbose_name='Enable Library Module'
    )
    
    enable_finance = models.BooleanField(
        default=True,
        verbose_name='Enable Finance Module'
    )
    
    enable_inventory = models.BooleanField(
        default=True,
        verbose_name='Enable Inventory Module'
    )

    enable_admission = models.BooleanField(
        default=True,
        verbose_name='Enable Admission Module'
    )
    
    enable_hr = models.BooleanField(
        default=True,
        verbose_name='Enable HR Module'
    )
    
    enable_transportation = models.BooleanField(
        default=True,
        verbose_name='Enable Transportation Module'
    )
    
    enable_hostel = models.BooleanField(
        default=True,
        verbose_name='Enable Hostel Module'
    )
    
    enable_exams = models.BooleanField(
        default=True,
        verbose_name='Enable Exams Module'
    )
    
    enable_assignments = models.BooleanField(
        default=True,
        verbose_name='Enable Assignments Module'
    )
    
    enable_communications = models.BooleanField(
        default=True,
        verbose_name='Enable Communications Module'
    )

    enable_events = models.BooleanField(
        default=True,
        verbose_name='Enable Events/Calendar Module'
    )
    
    # Custom Branding
    logo = models.ImageField(
        upload_to='tenant_logos/',
        null=True,
        blank=True,
        verbose_name='Organization Logo'
    )
    square_logo = models.ImageField(
        upload_to='tenant_logos/',
        null=True,
        blank=True,
        verbose_name='Organization Square Logo'
    )
    
    primary_color = models.CharField(
        max_length=7,
        default='#3B82F6',
        verbose_name='Primary Brand Color'
    )
    
    secondary_color = models.CharField(
        max_length=7,
        default='#1E40AF',
        verbose_name='Secondary Brand Color'
    )

    class Meta:
        db_table = 'tenant_configurations'
        verbose_name = 'Tenant Configuration'
        verbose_name_plural = 'Tenant Configurations'

    def __str__(self):
        return f"Configuration for {self.tenant.name}"

    def get_password_policy(self):
        """Get comprehensive password policy"""
        base_policy = {
            'min_length': 8,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_numbers': True,
            'require_special_chars': True,
            'prevent_common_passwords': True,
            'prevent_user_attributes': True,
            'expiry_days': self.password_expiry_days,
            'max_attempts': self.max_login_attempts,
        }
        
        # Merge with tenant-specific overrides
        if hasattr(self.tenant, 'password_policy'):
            base_policy.update(self.tenant.password_policy)
            
        return base_policy


    def get_available_modules(self):
        """Get list of enabled modules"""
        modules = []
        if self.enable_library:
            modules.append('library')
        if self.enable_finance:
            modules.append('finance')
        if self.enable_inventory:
            modules.append('inventory')
        return modules
    
    def validate_storage_limit(self, file_size_mb):
        """Check if file upload is within storage limits"""
        # Implement storage tracking logic
        current_usage = 0  # Get from storage tracking model
        return current_usage + file_size_mb <= self.tenant.max_storage_mb



class PaymentConfiguration(UUIDModel, TimeStampedModel):
    """
    Essential payment configuration for tenants
    """
    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name='payment_configuration',
        verbose_name='Tenant'
    )
    
    # Payment Status
    is_payments_enabled = models.BooleanField(
        default=False,
        verbose_name='Enable Payments'
    )
    
    # Razorpay (Primary for India)
    razorpay_key_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Razorpay Key ID'
    )
    
    razorpay_key_secret = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Razorpay Key Secret'
    )
    
    # Stripe (International)
    stripe_public_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Stripe Public Key'
    )
    
    stripe_secret_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Stripe Secret Key'
    )
    
    # Basic Settings
    currency = models.CharField(
        max_length=3,
        default='INR',
        verbose_name='Payment Currency'
    )
    
    is_test_mode = models.BooleanField(
        default=True,
        verbose_name='Test Mode'
    )

    class Meta:
        db_table = 'tenant_payment_configurations'
        verbose_name = 'Payment Configuration'

    def __str__(self):
        return f"Payment Config - {self.tenant.name}"
    
    @property
    def active_gateway(self):
        """Get active payment gateway"""
        if self.razorpay_key_id and self.razorpay_key_secret:
            return 'razorpay'
        elif self.stripe_public_key and self.stripe_secret_key:
            return 'stripe'
        return None


class AnalyticsConfiguration(UUIDModel, TimeStampedModel):
    """
    Essential analytics configuration for tenants
    """
    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name='analytics_configuration',
        verbose_name='Tenant'
    )
    
    # Google Analytics
    google_analytics_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Google Analytics ID'
    )
    
    # Microsoft Clarity
    clarity_project_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Clarity Project ID'
    )
    
    # Basic Settings
    anonymize_ip = models.BooleanField(
        default=True,
        verbose_name='Anonymize IP Addresses'
    )

    class Meta:
        db_table = 'tenant_analytics_configurations'
        verbose_name = 'Analytics Configuration'

    def __str__(self):
        return f"Analytics Config - {self.tenant.name}"
    
    @property
    def has_analytics(self):
        """Check if any analytics is configured"""
        return bool(self.google_analytics_id or self.clarity_project_id)


class SystemNotification(UUIDModel, TimeStampedModel):
    """
    Master Admin notifications sent to tenants
    """
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Target: Specific tenant or All (null = All)
    target_tenant = models.ForeignKey(
        'tenants.Tenant', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='system_notifications'
    )
    
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_system_notifications'
    )

    class Meta:
        db_table = 'tenant_system_notifications'
        verbose_name = 'System Notification'
        verbose_name_plural = 'System Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# ========== API KEY MANAGEMENT MODELS ==========

class APIServiceCategory(BaseModel):
    """Categories for API services"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Material icon name")
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'api_service_categories'
        verbose_name = 'API Service Category'
        verbose_name_plural = 'API Service Categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class APIService(BaseModel):
    """API Service definitions"""
    SERVICE_CLAUDE = 'claude'
    SERVICE_OPENAI = 'openai'
    SERVICE_GEMINI = 'gemini'
    SERVICE_MISTRAL = 'mistral'
    SERVICE_LLAMA = 'llama'
    SERVICE_WHATSAPP = 'whatsapp'
    SERVICE_TWILIO = 'twilio'
    SERVICE_TWILIO_SMS = 'twilio_sms'
    SERVICE_TWILIO_VOICE = 'twilio_voice'
    SERVICE_TWILIO_VIDEO = 'twilio_video'
    SERVICE_CLOUDINARY = 'cloudinary'
    SERVICE_AWS_S3 = 'aws_s3'
    SERVICE_AWS_REKOGNITION = 'aws_rekognition'
    SERVICE_AWS_POLLY = 'aws_polly'
    SERVICE_AWS_TRANSCRIBE = 'aws_transcribe'
    SERVICE_GOOGLE_VISION = 'google_vision'
    SERVICE_GOOGLE_SPEECH = 'google_speech'
    SERVICE_GOOGLE_TRANSLATE = 'google_translate'
    SERVICE_AZURE_AI = 'azure_ai'
    SERVICE_AZURE_SPEECH = 'azure_speech'
    SERVICE_AZURE_VISION = 'azure_vision'
    SERVICE_SENDGRID = 'sendgrid'
    SERVICE_MAILGUN = 'mailgun'
    SERVICE_STRIPE = 'stripe'
    SERVICE_RAZORPAY = 'razorpay'
    SERVICE_PAYPAL = 'paypal'
    SERVICE_GOOGLE_MAPS = 'google_maps'
    SERVICE_SMS_GATEWAY = 'sms_gateway'
    SERVICE_EMAIL_GATEWAY = 'email_gateway'
    SERVICE_PUSH_NOTIFICATION = 'push_notification'

    SERVICE_TYPES = [
        (SERVICE_CLAUDE, 'Anthropic Claude'),
        (SERVICE_OPENAI, 'OpenAI'),
        (SERVICE_GEMINI, 'Google Gemini'),
        (SERVICE_MISTRAL, 'Mistral AI'),
        (SERVICE_LLAMA, 'Meta Llama'),
        (SERVICE_WHATSAPP, 'WhatsApp Business'),
        (SERVICE_TWILIO, 'Twilio (General)'),
        (SERVICE_TWILIO_SMS, 'Twilio SMS'),
        (SERVICE_TWILIO_VOICE, 'Twilio Voice'),
        (SERVICE_TWILIO_VIDEO, 'Twilio Video'),
        (SERVICE_CLOUDINARY, 'Cloudinary'),
        (SERVICE_AWS_S3, 'AWS S3'),
        (SERVICE_AWS_REKOGNITION, 'AWS Rekognition'),
        (SERVICE_AWS_POLLY, 'AWS Polly'),
        (SERVICE_AWS_TRANSCRIBE, 'AWS Transcribe'),
        (SERVICE_GOOGLE_VISION, 'Google Vision'),
        (SERVICE_GOOGLE_SPEECH, 'Google Speech'),
        (SERVICE_GOOGLE_TRANSLATE, 'Google Translate'),
        (SERVICE_AZURE_AI, 'Azure AI'),
        (SERVICE_AZURE_SPEECH, 'Azure Speech'),
        (SERVICE_AZURE_VISION, 'Azure Vision'),
        (SERVICE_SENDGRID, 'SendGrid'),
        (SERVICE_MAILGUN, 'Mailgun'),
        (SERVICE_STRIPE, 'Stripe'),
        (SERVICE_RAZORPAY, 'Razorpay'),
        (SERVICE_PAYPAL, 'PayPal'),
        (SERVICE_GOOGLE_MAPS, 'Google Maps'),
        (SERVICE_SMS_GATEWAY, 'SMS Gateway'),
        (SERVICE_EMAIL_GATEWAY, 'Email Gateway'),
        (SERVICE_PUSH_NOTIFICATION, 'Push Notification'),
    ]

    SERVICE_CATEGORY_AI = 'ai'
    SERVICE_CATEGORY_COMMUNICATION = 'communication'
    SERVICE_CATEGORY_STORAGE = 'storage'
    SERVICE_CATEGORY_PAYMENT = 'payment'
    SERVICE_CATEGORY_MEDIA = 'media'
    SERVICE_CATEGORY_UTILITY = 'utility'

    SERVICE_CATEGORY_CHOICES = [
        (SERVICE_CATEGORY_AI, 'Artificial Intelligence'),
        (SERVICE_CATEGORY_COMMUNICATION, 'Communication'),
        (SERVICE_CATEGORY_STORAGE, 'Cloud Storage'),
        (SERVICE_CATEGORY_PAYMENT, 'Payment Gateway'),
        (SERVICE_CATEGORY_MEDIA, 'Media Processing'),
        (SERVICE_CATEGORY_UTILITY, 'Utility Services'),
    ]

    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES, unique=True)
    category = models.ForeignKey(APIServiceCategory, on_delete=models.PROTECT, related_name='services')
    description = models.TextField()
    base_url = models.URLField(blank=True, help_text="Base API URL")
    documentation_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    requires_auth = models.BooleanField(default=True)
    auth_type = models.CharField(
        max_length=20,
        choices=[
            ('api_key', 'API Key'),
            ('oauth2', 'OAuth 2.0'),
            ('jwt', 'JWT'),
            ('basic', 'Basic Auth'),
            ('bearer', 'Bearer Token'),
        ],
        default='api_key'
    )
    default_rate_limit = models.PositiveIntegerField(default=100, help_text="Requests per minute")
    icon = models.CharField(max_length=50, blank=True)
    config_schema = models.JSONField(default=dict, help_text="Configuration JSON schema")

    class Meta:
        db_table = 'api_services'
        verbose_name = 'API Service'
        verbose_name_plural = 'API Services'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_service_type_display()})"


class TenantAPIKey(UUIDModel, TimeStampedModel):
    """API Key management for tenants"""
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='api_keys',
        verbose_name='Tenant'
    )
    service = models.ForeignKey(
        APIService,
        on_delete=models.CASCADE,
        related_name='tenant_keys',
        verbose_name='API Service'
    )
    name = models.CharField(max_length=100, help_text="Display name for this key")
    
    # Encrypted API keys and secrets
    api_key = encrypt(models.CharField(max_length=500, verbose_name='API Key/Client ID'))
    api_secret = encrypt(models.TextField(blank=True, null=True, verbose_name='API Secret/Client Secret'))
    access_token = encrypt(models.TextField(blank=True, null=True))
    refresh_token = encrypt(models.TextField(blank=True, null=True))
    
    # Configuration (service-specific)
    config = models.JSONField(default=dict, help_text="Service-specific configuration")
    
    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    is_default = models.BooleanField(default=False, help_text="Use as default for this service")
    is_test_mode = models.BooleanField(default=True, help_text="Use test/sandbox environment")
    
    # Rate limiting
    rate_limit_per_minute = models.PositiveIntegerField(default=100)
    rate_limit_per_day = models.PositiveIntegerField(default=10000)
    
    # Usage tracking
    total_requests = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    # Expiry
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_api_keys'
    )
    
    class Meta:
        db_table = 'tenant_api_keys'
        verbose_name = 'Tenant API Key'
        verbose_name_plural = 'Tenant API Keys'
        unique_together = [['tenant', 'service', 'name']]
        indexes = [
            models.Index(fields=['tenant', 'service', 'is_active']),
            models.Index(fields=['tenant', 'is_default']),
        ]

    def __str__(self):
        return f"{self.tenant.name} - {self.service.name} - {self.name}"

    def clean(self):
        """Validate API key configuration"""
        from django.core.exceptions import ValidationError
        
        super().clean()
        
        # Ensure only one default key per service per tenant
        if self.is_default and self.is_active:
            existing_default = TenantAPIKey.objects.filter(
                tenant=self.tenant,
                service=self.service,
                is_default=True,
                is_active=True
            ).exclude(id=self.id)
            
            if existing_default.exists():
                raise ValidationError({
                    'is_default': 'Only one active default key is allowed per service per tenant.'
                })

    def rotate_key(self, new_key, new_secret=None):
        """Rotate API key"""
        old_key = self.api_key
        self.api_key = new_key
        if new_secret:
            self.api_secret = new_secret
        self.save()
        
        # Log the rotation
        self.tenant.audit_log(
            'API_KEY_ROTATED',
            user=self.created_by,
            metadata={
                'service': self.service.name,
                'key_id': str(self.id)
            },
            severity='MEDIUM'
        )
        
        return True

    def deactivate(self, reason="Manual deactivation"):
        """Deactivate API key"""
        self.is_active = False
        self.save()
        
        self.tenant.audit_log(
            'API_KEY_DEACTIVATED',
            user=self.created_by,
            metadata={
                'service': self.service.name,
                'key_id': str(self.id),
                'reason': reason
            },
            severity='MEDIUM'
        )

    @property
    def masked_key(self):
        """Return masked API key for display"""
        if self.api_key:
            key = str(self.api_key)
            if len(key) > 8:
                return f"{key[:4]}...{key[-4:]}"
        return "********"

    @property
    def is_expired(self):
        """Check if key is expired"""
        from django.utils import timezone
        return self.expires_at and self.expires_at < timezone.now()


class APIUsageLog(UUIDModel, TimeStampedModel):
    """API usage tracking"""
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='api_usage_logs',
        verbose_name='Tenant'
    )
    api_key = models.ForeignKey(
        TenantAPIKey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usage_logs'
    )
    service = models.ForeignKey(
        APIService,
        on_delete=models.CASCADE,
        related_name='usage_logs'
    )
    
    # Request details
    endpoint = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    status_code = models.PositiveIntegerField()
    request_count = models.PositiveIntegerField(default=1)
    
    # Response details
    response_time_ms = models.PositiveIntegerField(help_text="Response time in milliseconds")
    response_size_bytes = models.PositiveIntegerField(default=0)
    
    # Cost tracking (if applicable)
    cost_units = models.DecimalField(max_digits=12, decimal_places=6, default=0)
    
    # Error tracking
    error_code = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)
    
    # Metadata
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = 'api_usage_logs'
        verbose_name = 'API Usage Log'
        verbose_name_plural = 'API Usage Logs'
        indexes = [
            models.Index(fields=['tenant', 'service', 'created_at']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status_code']),
        ]

    def __str__(self):
        return f"{self.tenant.name} - {self.service.name} - {self.endpoint} - {self.created_at}"

    @classmethod
    def log_request(cls, tenant, service, endpoint, method, status_code, **kwargs):
        """Helper to log API request"""
        return cls.objects.create(
            tenant=tenant,
            service=service,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            **kwargs
        )


class TenantSecret(UUIDModel, TimeStampedModel):
    """Secure storage for sensitive tenant data"""
    SECRET_TYPE_DATABASE = 'database'
    SECRET_TYPE_SSH = 'ssh'
    SECRET_TYPE_CERTIFICATE = 'certificate'
    SECRET_TYPE_ENCRYPTION = 'encryption'
    SECRET_TYPE_OTHER = 'other'
    
    SECRET_TYPE_CHOICES = [
        (SECRET_TYPE_DATABASE, 'Database Credentials'),
        (SECRET_TYPE_SSH, 'SSH Keys'),
        (SECRET_TYPE_CERTIFICATE, 'SSL Certificate'),
        (SECRET_TYPE_ENCRYPTION, 'Encryption Keys'),
        (SECRET_TYPE_OTHER, 'Other'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='secrets',
        verbose_name='Tenant'
    )
    
    name = models.CharField(max_length=100)
    secret_type = models.CharField(max_length=50, choices=SECRET_TYPE_CHOICES)
    
    # Encrypted fields
    secret_value = encrypt(models.TextField())
    secret_value_encrypted = models.BinaryField(blank=True, null=True)  # Alternative encryption
    
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list, help_text="Tags for categorization")
    
    # Expiry and rotation
    expires_at = models.DateTimeField(null=True, blank=True)
    rotation_interval_days = models.PositiveIntegerField(default=90, help_text="Days between rotations")
    last_rotated_at = models.DateTimeField(null=True, blank=True)
    
    # Access control
    is_encrypted = models.BooleanField(default=True)
    can_decrypt_users = models.ManyToManyField(
        'users.User',
        blank=True,
        related_name='accessible_secrets',
        help_text="Users who can decrypt this secret"
    )
    
    # Audit
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_secrets'
    )

    class Meta:
        db_table = 'tenant_secrets'
        verbose_name = 'Tenant Secret'
        verbose_name_plural = 'Tenant Secrets'
        indexes = [
            models.Index(fields=['tenant', 'secret_type']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.tenant.name} - {self.name} ({self.get_secret_type_display()})"

    def rotate(self, new_value):
        """Rotate secret value"""
        old_value = self.secret_value
        self.secret_value = new_value
        self.last_rotated_at = timezone.now()
        self.save()
        
        self.tenant.audit_log(
            'SECRET_ROTATED',
            user=self.created_by,
            metadata={
                'secret_id': str(self.id),
                'secret_type': self.secret_type,
                'name': self.name
            },
            severity='HIGH'
        )

    @property
    def needs_rotation(self):
        """Check if secret needs rotation"""
        from django.utils import timezone
        if not self.last_rotated_at:
            return False
        rotation_date = self.last_rotated_at + timezone.timedelta(days=self.rotation_interval_days)
        return timezone.now() > rotation_date

    @property
    def is_expired(self):
        """Check if secret is expired"""
        from django.utils import timezone
        return self.expires_at and self.expires_at < timezone.now()


class VideoAPIKey(TenantAPIKey):
    """Specialized model for video API keys"""
    class Meta:
        proxy = True
        verbose_name = 'Video API Key'
        verbose_name_plural = 'Video API Keys'

    def get_service_type(self):
        return [
            APIService.SERVICE_TWILIO_VIDEO,
            APIService.SERVICE_CLOUDINARY,
        ]


class WhatsAppAPIKey(TenantAPIKey):
    """Specialized model for WhatsApp Business API"""
    class Meta:
        proxy = True
        verbose_name = 'WhatsApp API Key'
        verbose_name_plural = 'WhatsApp API Keys'

    def get_service_type(self):
        return [APIService.SERVICE_WHATSAPP]


class SMSAPIKey(TenantAPIKey):
    """Specialized model for SMS gateway APIs"""
    class Meta:
        proxy = True
        verbose_name = 'SMS API Key'
        verbose_name_plural = 'SMS API Keys'

    def get_service_type(self):
        return [
            APIService.SERVICE_TWILIO_SMS,
            APIService.SERVICE_SMS_GATEWAY,
        ]


class AIAPIKey(TenantAPIKey):
    """Specialized model for AI/ML APIs"""
    class Meta:
        proxy = True
        verbose_name = 'AI API Key'
        verbose_name_plural = 'AI API Keys'

    def get_service_type(self):
        return [
            APIService.SERVICE_CLAUDE,
            APIService.SERVICE_OPENAI,
            APIService.SERVICE_GEMINI,
            APIService.SERVICE_MISTRAL,
            APIService.SERVICE_LLAMA,
            APIService.SERVICE_AZURE_AI,
        ]


class TenantAddress(UUIDModel, TimeStampedModel):
    """
    Physical address for the tenant organization
    """
    tenant = models.OneToOneField(
        Tenant,
        on_delete=models.CASCADE,
        related_name='address',
        verbose_name='Tenant'
    )
    
    address_line_1 = models.CharField(
        max_length=255,
        verbose_name='Address Line 1'
    )
    
    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Address Line 2'
    )
    
    city = models.CharField(
        max_length=100,
        verbose_name='City'
    )
    
    state = models.CharField(
        max_length=100,
        verbose_name='State/Province'
    )
    
    postal_code = models.CharField(
        max_length=20,
        verbose_name='Postal/Zip Code'
    )
    
    country = models.CharField(
        max_length=100,
        default='India',
        verbose_name='Country'
    )

    class Meta:
        db_table = 'tenant_addresses'
        verbose_name = 'Tenant Address'
        verbose_name_plural = 'Tenant Addresses'

    def __str__(self):
        return f"Address - {self.tenant.name}"
    
    @property
    def full_address(self):
        """Format full address string"""
        parts = [self.address_line_1]
        if self.address_line_2:
            parts.append(self.address_line_2)
        parts.append(f"{self.city}, {self.state} - {self.postal_code}")
        parts.append(self.country)
        return ", ".join(parts)
