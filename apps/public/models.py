from django.db import models
from apps.core.models import BaseSharedModel

class FeatureModule(BaseSharedModel):
    """
    Dynamic feature modules displayed on the home page
    """
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Bootstrap Icon class (e.g., 'bi-people')")
    display_order = models.PositiveIntegerField(default=0)
    
    # Visual styling
    color_class = models.CharField(
        max_length=20, 
        choices=[
            ('primary', 'Blue'),
            ('success', 'Green'),
            ('warning', 'Yellow'),
            ('danger', 'Red'),
            ('info', 'Cyan'),
            ('dark', 'Dark'),
        ],
        default='primary'
    )

    class Meta:
        ordering = ['display_order', 'title']
        verbose_name = 'Feature Module'
        verbose_name_plural = 'Feature Modules'

    def __str__(self):
        return self.title


class PricingPlan(BaseSharedModel):
    """
    Pricing plans displayed on the public site
    """
    PLAN_INTERVALS = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('one_time', 'One Time'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    interval = models.CharField(max_length=20, choices=PLAN_INTERVALS, default='monthly')
    description = models.TextField(blank=True)
    
    is_popular = models.BooleanField(default=False)
    highlight_text = models.CharField(max_length=50, blank=True, help_text="e.g. 'Most Value'")
    
    button_text = models.CharField(max_length=50, default='Get Started')
    button_link = models.CharField(max_length=200, default='#')

    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'price']
        verbose_name = 'Pricing Plan'
        verbose_name_plural = 'Pricing Plans'

    def __str__(self):
        return f"{self.name} - {self.price}"


class PricingFeature(BaseSharedModel):
    """
    Features list item for a specific pricing plan
    """
    plan = models.ForeignKey(PricingPlan, on_delete=models.CASCADE, related_name='features')
    text = models.CharField(max_length=255)
    is_included = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'id']
        verbose_name = 'Pricing Feature'
        verbose_name_plural = 'Pricing Features'

    def __str__(self):
        return f"{self.plan.name} - {self.text}"


class DemoRequest(BaseSharedModel):
    """
    Requests for product demos
    """
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('scheduled', 'Demo Scheduled'),
        ('completed', 'Demo Completed'),
        ('converted', 'Converted'),
        ('closed', 'Closed'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    institution_name = models.CharField(max_length=200)
    role = models.CharField(max_length=100, blank=True)
    message = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Demo Request'
        verbose_name_plural = 'Demo Requests'

    def __str__(self):
        return f"{self.name} - {self.institution_name}"


class ContactRequest(BaseSharedModel):
    """
    General contact inquiries
    """
    STATUS_CHOICES = [
        ('new', 'New'),
        ('responded', 'Responded'),
        ('spam', 'Spam'),
        ('closed', 'Closed'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Request'
        verbose_name_plural = 'Contact Requests'

    def __str__(self):
        return f"{self.email} - {self.subject}"
