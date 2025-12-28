from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from .models import (
    Tenant,
    Domain,
    TenantConfiguration,
    APIServiceCategory,
    APIService,
    TenantAPIKey,
)


# ---------------------------------------------------------
# Create default tenant configuration
# ---------------------------------------------------------
@receiver(post_save, sender=Tenant)
def create_tenant_configuration(sender, instance, created, **kwargs):
    """Create default configuration for new tenants"""
    if created:
        TenantConfiguration.objects.get_or_create(tenant=instance)


# ---------------------------------------------------------
# Validate primary domain
# ---------------------------------------------------------
@receiver(pre_save, sender=Domain)
def validate_primary_domain(sender, instance, **kwargs):
    """Ensure primary domain is verified before saving"""
    if instance.is_primary and not instance.is_verified:
        raise ValidationError("Primary domain must be verified")


# ---------------------------------------------------------
# Create default API categories & services
# ---------------------------------------------------------
@receiver(post_save, sender=Tenant)
def create_default_api_services(sender, instance, created, **kwargs):
    """Create default API categories and services for tenants"""
    if not created:
        return

    # Default service categories
    categories = [
        ('Artificial Intelligence', 1),
        ('Communication', 2),
        ('Cloud Storage', 3),
        ('Payment Gateway', 4),
        ('Media Processing', 5),
    ]

    for name, order in categories:
        APIServiceCategory.objects.get_or_create(
            name=name,
            defaults={'display_order': order}
        )

    # Default API services
    default_services = [
        {
            'name': 'Cloudinary',
            'service_type': APIService.SERVICE_CLOUDINARY,
            'category': APIServiceCategory.objects.get(name='Media Processing'),
            'description': 'Cloud-based image and video management',
            'base_url': 'https://api.cloudinary.com/v1_1/',
        },
        {
            'name': 'OpenAI',
            'service_type': APIService.SERVICE_OPENAI,
            'category': APIServiceCategory.objects.get(name='Artificial Intelligence'),
            'description': 'OpenAI GPT models API',
            'base_url': 'https://api.openai.com/v1/',
        },
        {
            'name': 'WhatsApp Business',
            'service_type': APIService.SERVICE_WHATSAPP,
            'category': APIServiceCategory.objects.get(name='Communication'),
            'description': 'WhatsApp Business API',
            'base_url': 'https://graph.facebook.com/v17.0/',
        },
    ]

    for service in default_services:
        APIService.objects.get_or_create(
            service_type=service['service_type'],
            defaults=service
        )


# ---------------------------------------------------------
# Ensure only one default API key per service per tenant
# ---------------------------------------------------------
@receiver(pre_save, sender=TenantAPIKey)
def ensure_one_default_key(sender, instance, **kwargs):
    """Ensure only one default API key per service per tenant"""
    if instance.is_default and instance.is_active:
        TenantAPIKey.objects.filter(
            tenant=instance.tenant,
            service=instance.service,
            is_default=True
        ).exclude(pk=instance.pk).update(is_default=False)
