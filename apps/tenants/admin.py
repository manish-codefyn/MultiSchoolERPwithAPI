from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from .models import (
    Tenant, Domain, TenantConfiguration, PaymentConfiguration, 
    AnalyticsConfiguration, SystemNotification, APIServiceCategory, 
    APIService, TenantAPIKey, APIUsageLog, TenantSecret
)

@admin.register(Tenant)
class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'schema_name', 'status', 'plan', 'is_active', 'created_at')
    list_filter = ('status', 'plan', 'is_active')
    search_fields = ('name', 'schema_name', 'contact_email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Organization Info', {
            'fields': ('name', 'display_name', 'slug', 'contact_email', 'contact_phone')
        }),
        ('Technical Info', {
            'fields': ('schema_name', 'auto_create_schema')
        }),
        ('Subscription & Status', {
            'fields': ('status', 'plan', 'is_active', 'trial_ends_at', 'subscription_ends_at')
        }),
        ('Limits', {
            'fields': ('max_users', 'max_storage_mb')
        }),
        ('Security', {
            'fields': ('force_password_reset', 'mfa_required', 'password_policy')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('schema_name',)
        return self.readonly_fields

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary', 'is_verified', 'ssl_enabled')
    list_filter = ('is_primary', 'is_verified', 'ssl_enabled')
    search_fields = ('domain', 'tenant__name')

@admin.register(TenantConfiguration)
class TenantConfigurationAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'enable_library', 'enable_finance', 'enable_inventory')
    list_filter = ('enable_library', 'enable_finance', 'enable_inventory')
    search_fields = ('tenant__name',)

@admin.register(PaymentConfiguration)
class PaymentConfigurationAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'is_payments_enabled', 'currency', 'is_test_mode')
    list_filter = ('is_payments_enabled', 'is_test_mode')
    search_fields = ('tenant__name', 'razorpay_key_id')

@admin.register(AnalyticsConfiguration)
class AnalyticsConfigurationAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'google_analytics_id', 'clarity_project_id', 'anonymize_ip')
    list_filter = ('anonymize_ip',)
    search_fields = ('tenant__name', 'google_analytics_id', 'clarity_project_id')

@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_tenant', 'is_active', 'expires_at', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'message', 'target_tenant__name')
    raw_id_fields = ('target_tenant', 'created_by')

@admin.register(APIServiceCategory)
class APIServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_order', 'icon')
    search_fields = ('name',)
    ordering = ('display_order', 'name')

@admin.register(APIService)
class APIServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'service_type', 'is_active', 'requires_auth')
    list_filter = ('category', 'service_type', 'is_active', 'requires_auth')
    search_fields = ('name', 'description')
    ordering = ('category', 'name')

@admin.register(TenantAPIKey)
class TenantAPIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'service', 'key_preview', 'is_active', 'expires_at')
    list_filter = ('service', 'is_active', 'is_default')
    search_fields = ('name', 'tenant__name')
    readonly_fields = ('key_preview', 'created_at', 'last_used_at')
    
    def key_preview(self, obj):
        if not obj:
            return "-"
        return obj.masked_key
    key_preview.short_description = 'API Key'

@admin.register(APIUsageLog)
class APIUsageLogAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'service', 'endpoint', 'method', 'status_code', 'created_at')
    list_filter = ('service', 'method', 'status_code', 'created_at')
    search_fields = ('tenant__name', 'endpoint')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(TenantSecret)
class TenantSecretAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'secret_type', 'expires_at', 'is_expired')
    list_filter = ('secret_type', 'created_at')
    search_fields = ('name', 'tenant__name')
    readonly_fields = ('created_at', 'updated_at')
