from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tenants', views.TenantViewSet)
router.register(r'domains', views.DomainViewSet)
router.register(r'tenantconfigurations', views.TenantConfigurationViewSet)
router.register(r'paymentconfigurations', views.PaymentConfigurationViewSet)
router.register(r'analyticsconfigurations', views.AnalyticsConfigurationViewSet)
router.register(r'systemnotifications', views.SystemNotificationViewSet)
router.register(r'apiservicecategorys', views.APIServiceCategoryViewSet)
router.register(r'apiservices', views.APIServiceViewSet)
router.register(r'tenantapikeys', views.TenantAPIKeyViewSet)
router.register(r'apiusagelogs', views.APIUsageLogViewSet)
router.register(r'tenantsecrets', views.TenantSecretViewSet)
router.register(r'videoapikeys', views.VideoAPIKeyViewSet)
router.register(r'whatsappapikeys', views.WhatsAppAPIKeyViewSet)
router.register(r'smsapikeys', views.SMSAPIKeyViewSet)
router.register(r'aiapikeys', views.AIAPIKeyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
