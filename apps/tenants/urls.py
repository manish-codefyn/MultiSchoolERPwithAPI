
from django.urls import path
from . import views

app_name = "tenants"

urlpatterns = [
    path('dashboard/', views.TenantDashboardView.as_view(), name='dashboard'),
    
    # Tenants
    path('dsd/', views.TenantListView.as_view(), name='home'),
    path('tenant_list/', views.TenantListView.as_view(), name='tenant_list'),
    path('<uuid:pk>/', views.TenantDetailView.as_view(), name='tenant_detail'),
    path('create/', views.TenantCreateView.as_view(), name='tenant_create'),
    path('<uuid:pk>/update/', views.TenantUpdateView.as_view(), name='tenant_update'),
    path('<uuid:pk>/delete/', views.TenantDeleteView.as_view(), name='tenant_delete'),
    
    # Domains
    path('domains/', views.DomainListView.as_view(), name='domain_list'),
    path('domains/create/', views.DomainCreateView.as_view(), name='domain_create'),
    path('domains/<uuid:pk>/update/', views.DomainUpdateView.as_view(), name='domain_update'),
    path('domains/<uuid:pk>/delete/', views.DomainDeleteView.as_view(), name='domain_delete'),
    
    # Configurations
    path('<uuid:pk>/configuration/', views.TenantConfigurationUpdateView.as_view(), name='tenant_config'),
    path('<uuid:pk>/address/', views.TenantAddressUpdateView.as_view(), name='address_config'),
    path('<uuid:pk>/payment-config/', views.PaymentConfigurationUpdateView.as_view(), name='payment_config'),
    path('<uuid:pk>/analytics-config/', views.AnalyticsConfigurationUpdateView.as_view(), name='analytics_config'),
    
    # Global Explorer
    path('users/global/', views.GlobalUserListView.as_view(), name='global_user_list'),
    path('students/global/', views.GlobalStudentListView.as_view(), name='global_student_list'),
    
    # System Notifications
    path('notifications/', views.SystemNotificationListView.as_view(), name='notification_list'),
    path('notifications/send/', views.SystemNotificationCreateView.as_view(), name='notification_create'),

    # API Services
    path('services/', views.APIServiceListView.as_view(), name='service_list'),
    path('services/create/', views.APIServiceCreateView.as_view(), name='service_create'),
    path('services/<uuid:pk>/update/', views.APIServiceUpdateView.as_view(), name='service_update'),
    
    # API Keys
    path('api-keys/', views.TenantAPIKeyListView.as_view(), name='apikey_list'),
    path('api-keys/create/', views.TenantAPIKeyCreateView.as_view(), name='apikey_create'),
    path('api-keys/<uuid:pk>/update/', views.TenantAPIKeyUpdateView.as_view(), name='apikey_update'),
    
    # Tenant Secrets
    path('secrets/', views.TenantSecretListView.as_view(), name='secret_list'),
    path('secrets/create/', views.TenantSecretCreateView.as_view(), name='secret_create'),
    path('secrets/<uuid:pk>/update/', views.TenantSecretUpdateView.as_view(), name='secret_update'),
    
    # API Usage Logs
    # API Usage Logs
    path('api-usage/', views.APIUsageLogListView.as_view(), name='api_usage_list'),
    
    # Audit Logs
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit_log_list'),
]
