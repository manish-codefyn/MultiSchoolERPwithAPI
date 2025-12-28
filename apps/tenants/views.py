from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count, Q
from django_tenants.utils import schema_context
from apps.core.permissions.mixins import PermissionRequiredMixin
from .models import Tenant, Domain, TenantConfiguration, PaymentConfiguration, AnalyticsConfiguration, SystemNotification, APIService, APIServiceCategory, TenantAPIKey, TenantSecret, APIUsageLog
from apps.security.models import AuditLog
from apps.users.models import User
from apps.students.models import Student

class SuperuserRequiredMixin(LoginRequiredMixin):
    """Limit access to superusers only"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

from django.core.exceptions import PermissionDenied

class TenantDashboardView(SuperuserRequiredMixin, TemplateView):
    template_name = 'tenants/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['total_tenants'] = Tenant.objects.count()
        context['active_tenants'] = Tenant.objects.filter(status='active', is_active=True).count()
        context['trial_tenants'] = Tenant.objects.filter(status='trial').count()
        context['suspended_tenants'] = Tenant.objects.filter(status='suspended').count()
        
        # Calculate per-tenant stats
        tenant_stats = []
        tenants = Tenant.objects.exclude(schema_name='public').order_by('name')
        
        for tenant in tenants:
            with schema_context(tenant.schema_name):
                # Use all_objects to bypass UserManager's current_tenant filter
                user_count = User.all_objects.filter(tenant=tenant).count()
                # Use cross_tenant() to bypass TenantManager's current_tenant filter
                # and explicitly filter active student
                student_count = Student.objects.cross_tenant().filter(is_active=True).count()
                
                tenant_stats.append({
                    'name': tenant.name,
                    'schema_name': tenant.schema_name,
                    'onboarding_status': tenant.onboarding_status,
                    'user_count': user_count,
                    'student_count': student_count,
                    'pk': tenant.pk
                })
        
        context['tenant_stats'] = tenant_stats
        
        return context

# ==================== TENANT ====================

class TenantListView(SuperuserRequiredMixin, ListView):
    model = Tenant
    template_name = 'tenants/tenant_list.html'
    context_object_name = 'tenants'

class TenantDetailView(SuperuserRequiredMixin, DetailView):
    model = Tenant
    template_name = 'tenants/tenant_detail.html'
    context_object_name = 'tenant'

class TenantCreateView(SuperuserRequiredMixin, CreateView):
    model = Tenant
    fields = ['name', 'display_name', 'schema_name', 'status', 'onboarding_status', 'plan', 'max_users', 
              'max_storage_mb', 'contact_email', 'contact_phone', 'is_active']
    template_name = 'tenants/tenant_form.html'
    success_url = reverse_lazy('tenants:tenant_list')

    def form_valid(self, form):
        messages.success(self.request, "Tenant created successfully.")
        return super().form_valid(form)

class TenantUpdateView(SuperuserRequiredMixin, UpdateView):
    model = Tenant
    fields = ['name', 'display_name', 'status', 'onboarding_status', 'plan', 'max_users', 
              'max_storage_mb', 'contact_email', 'contact_phone', 'is_active']
    template_name = 'tenants/tenant_form.html'
    success_url = reverse_lazy('tenants:tenant_list')

    def form_valid(self, form):
        messages.success(self.request, "Tenant updated successfully.")
        return super().form_valid(form)

class TenantDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Tenant
    template_name = 'tenants/confirm_delete.html'
    success_url = reverse_lazy('tenants:tenant_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Tenant deleted successfully.")
        return super().delete(request, *args, **kwargs)

# ==================== DOMAIN ====================

class DomainListView(SuperuserRequiredMixin, ListView):
    model = Domain
    template_name = 'tenants/domain_list.html'
    context_object_name = 'domains'

class DomainCreateView(SuperuserRequiredMixin, CreateView):
    model = Domain
    fields = ['tenant', 'domain', 'is_primary', 'ssl_enabled']
    template_name = 'tenants/domain_form.html'
    success_url = reverse_lazy('tenants:domain_list')

    def form_valid(self, form):
        messages.success(self.request, "Domain created successfully.")
        return super().form_valid(form)

class DomainUpdateView(SuperuserRequiredMixin, UpdateView):
    model = Domain
    fields = ['tenant', 'domain', 'is_primary', 'ssl_enabled', 'is_verified']
    template_name = 'tenants/domain_form.html'
    success_url = reverse_lazy('tenants:domain_list')

    def form_valid(self, form):
        messages.success(self.request, "Domain updated successfully.")
        return super().form_valid(form)

class DomainDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Domain
    template_name = 'tenants/confirm_delete.html'
    success_url = reverse_lazy('tenants:domain_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Domain deleted successfully.")
        return super().delete(request, *args, **kwargs)


# ==================== CONFIGURATIONS ====================

class TenantConfigurationUpdateView(SuperuserRequiredMixin, UpdateView):
    model = TenantConfiguration
    fields = [
        'academic_year', 'timezone', 'language', 'currency', 'date_format',
        'session_timeout', 'max_login_attempts', 'password_expiry_days',
        'enable_library', 'enable_finance', 'enable_inventory',
        'logo', 'primary_color', 'secondary_color'
    ]
    template_name = 'tenants/config_form.html'
    
    def get_object(self, queryset=None):
        return TenantConfiguration.objects.get_or_create(tenant_id=self.kwargs.get('pk'))[0]

    def get_success_url(self):
        return reverse_lazy('tenants:tenant_detail', kwargs={'pk': self.kwargs.get('pk')})

    def form_valid(self, form):
        messages.success(self.request, "Tenant Configuration updated successfully.")
        return super().form_valid(form)


class PaymentConfigurationUpdateView(SuperuserRequiredMixin, UpdateView):
    model = PaymentConfiguration
    fields = [
        'is_payments_enabled', 'razorpay_key_id', 'razorpay_key_secret',
        'stripe_public_key', 'stripe_secret_key', 'currency', 'is_test_mode'
    ]
    template_name = 'tenants/config_form.html'

    def get_object(self, queryset=None):
        return PaymentConfiguration.objects.get_or_create(tenant_id=self.kwargs.get('pk'))[0]

    def get_success_url(self):
        return reverse_lazy('tenants:tenant_detail', kwargs={'pk': self.kwargs.get('pk')})

    def form_valid(self, form):
        messages.success(self.request, "Payment Configuration updated successfully.")
        return super().form_valid(form)


class AnalyticsConfigurationUpdateView(SuperuserRequiredMixin, UpdateView):
    model = AnalyticsConfiguration
    fields = ['google_analytics_id', 'clarity_project_id', 'anonymize_ip']
    template_name = 'tenants/config_form.html'

    def get_object(self, queryset=None):
        return AnalyticsConfiguration.objects.get_or_create(tenant_id=self.kwargs.get('pk'))[0]

    def get_success_url(self):
        return reverse_lazy('tenants:tenant_detail', kwargs={'pk': self.kwargs.get('pk')})

    def form_valid(self, form):
        messages.success(self.request, "Analytics Configuration updated successfully.")
        return super().form_valid(form)


# ==================== GLOBAL EXPLORER ====================

class GlobalUserListView(SuperuserRequiredMixin, ListView):
    model = User
    template_name = 'tenants/global_user_list.html'
    context_object_name = 'users'


    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')


class GlobalStudentListView(SuperuserRequiredMixin, TemplateView):
    template_name = 'tenants/global_student_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_students = []
        tenants = Tenant.objects.exclude(schema_name='public')
        
        for tenant in tenants:
            with schema_context(tenant.schema_name):
                students = list(Student.objects.all().values(
                    'first_name', 'last_name', 'reg_no', 'status'
                ))
                for s in students:
                    s['tenant_name'] = tenant.name
                    all_students.append(s)
        
        context['students'] = all_students
        return context


# ==================== SYSTEM NOTIFICATIONS ====================

class SystemNotificationListView(SuperuserRequiredMixin, ListView):
    model = SystemNotification
    template_name = 'tenants/notification_list.html'
    context_object_name = 'notifications'


class SystemNotificationCreateView(SuperuserRequiredMixin, CreateView):
    model = SystemNotification
    fields = ['title', 'message', 'target_tenant', 'expires_at', 'is_active']
    template_name = 'tenants/notification_form.html'
    success_url = reverse_lazy('tenants:notification_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "System Notification sent successfully.")
        return super().form_valid(form)


# ==================== API SERVICES ====================

class APIServiceListView(SuperuserRequiredMixin, ListView):
    model = APIService
    template_name = 'tenants/service_list.html'
    context_object_name = 'services'

    def get_queryset(self):
        return APIService.objects.select_related('category').all().order_by('category', 'name')


class APIServiceCreateView(SuperuserRequiredMixin, CreateView):
    model = APIService
    fields = ['name', 'service_type', 'category', 'description', 'base_url', 'documentation_url', 
              'is_active', 'requires_auth', 'auth_type', 'default_rate_limit', 'icon']
    template_name = 'tenants/service_form.html'
    success_url = reverse_lazy('tenants:service_list')

    def form_valid(self, form):
        messages.success(self.request, "API Service created successfully.")
        return super().form_valid(form)


class APIServiceUpdateView(SuperuserRequiredMixin, UpdateView):
    model = APIService
    fields = ['name', 'service_type', 'category', 'description', 'base_url', 'documentation_url', 
              'is_active', 'requires_auth', 'auth_type', 'default_rate_limit', 'icon']
    template_name = 'tenants/service_form.html'
    success_url = reverse_lazy('tenants:service_list')

    def form_valid(self, form):
        messages.success(self.request, "API Service updated successfully.")
        return super().form_valid(form)


# ==================== TENANT API KEYS ====================

class TenantAPIKeyListView(SuperuserRequiredMixin, ListView):
    model = TenantAPIKey
    template_name = 'tenants/apikey_list.html'
    context_object_name = 'api_keys'

    def get_queryset(self):
        queryset = TenantAPIKey.objects.select_related('tenant', 'service').all()
        tenant_id = self.request.GET.get('tenant')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        return queryset


class TenantAPIKeyCreateView(SuperuserRequiredMixin, CreateView):
    model = TenantAPIKey
    fields = ['tenant', 'service', 'name', 'api_key', 'api_secret', 
              'is_active', 'is_default', 'is_test_mode', 'rate_limit_per_minute']
    template_name = 'tenants/apikey_form.html'
    success_url = reverse_lazy('tenants:apikey_list')

    def get_initial(self):
        initial = super().get_initial()
        tenant_id = self.request.GET.get('tenant')
        if tenant_id:
            initial['tenant'] = tenant_id
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "API Key created successfully.")
        return super().form_valid(form)


class TenantAPIKeyUpdateView(SuperuserRequiredMixin, UpdateView):
    model = TenantAPIKey
    fields = ['tenant', 'service', 'name', 'api_key', 'api_secret', 
              'is_active', 'is_default', 'is_test_mode', 'rate_limit_per_minute']
    template_name = 'tenants/apikey_form.html'
    success_url = reverse_lazy('tenants:apikey_list')

    def form_valid(self, form):
        messages.success(self.request, "API Key updated successfully.")
        return super().form_valid(form)


# ==================== TENANT SECRETS ====================

class TenantSecretListView(SuperuserRequiredMixin, ListView):
    model = TenantSecret
    template_name = 'tenants/secret_list.html'
    context_object_name = 'secrets'

    def get_queryset(self):
        queryset = TenantSecret.objects.select_related('tenant').all()
        tenant_id = self.request.GET.get('tenant')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        return queryset


class TenantSecretCreateView(SuperuserRequiredMixin, CreateView):
    model = TenantSecret
    fields = ['tenant', 'name', 'secret_type', 'secret_value', 'description', 
              'tags', 'rotation_interval_days', 'is_encrypted']
    template_name = 'tenants/secret_form.html'
    success_url = reverse_lazy('tenants:secret_list')

    def get_initial(self):
        initial = super().get_initial()
        tenant_id = self.request.GET.get('tenant')
        if tenant_id:
            initial['tenant'] = tenant_id
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Secret created successfully.")
        return super().form_valid(form)


class TenantSecretUpdateView(SuperuserRequiredMixin, UpdateView):
    model = TenantSecret
    fields = ['tenant', 'name', 'secret_type', 'secret_value', 'description', 
              'tags', 'rotation_interval_days', 'is_encrypted']
    template_name = 'tenants/secret_form.html'
    success_url = reverse_lazy('tenants:secret_list')

    def form_valid(self, form):
        messages.success(self.request, "Secret updated successfully.")
        return super().form_valid(form)


# ==================== API USAGE LOGS ====================

class APIUsageLogListView(SuperuserRequiredMixin, ListView):
    model = APIUsageLog
    template_name = 'tenants/api_usage_list.html'
    context_object_name = 'usage_logs'
    paginate_by = 50

    def get_queryset(self):
        queryset = APIUsageLog.objects.select_related('tenant', 'service', 'api_key').all().order_by('-created_at')
        
        # Filtering
        tenant_id = self.request.GET.get('tenant')
        service_id = self.request.GET.get('service')
        
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        if service_id:
            queryset = queryset.filter(service_id=service_id)
            
        return queryset


class TenantConfigurationUpdateView(SuperuserRequiredMixin, UpdateView):
    model = TenantConfiguration
    fields = ['academic_year', 'timezone', 'language', 'currency', 'date_format',
              'session_timeout', 'max_login_attempts', 'password_expiry_days',
              'enable_library', 'enable_finance', 'enable_inventory',
              'logo', 'primary_color', 'secondary_color']
    template_name = 'tenants/tenant_configuration_form.html'
    
    def get_object(self, queryset=None):
        # Get configuration for the specific tenant
        tenant_id = self.kwargs.get('pk')
        return TenantConfiguration.objects.get(tenant_id=tenant_id)
        
    def get_success_url(self):
        messages.success(self.request, "Tenant configuration updated successfully.")
        return reverse_lazy('tenants:tenant_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tenant'] = self.object.tenant
        return context


class AuditLogListView(SuperuserRequiredMixin, ListView):
    model = AuditLog
    template_name = 'tenants/audit_log_list.html'
    context_object_name = 'audit_logs'
    paginate_by = 50
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtering
        event_type = self.request.GET.get('event_type')
        user_id = self.request.GET.get('user')
        
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        return queryset
