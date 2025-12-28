from django.views.generic import ListView, DetailView
from django.shortcuts import render
from django.db import connection, transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from apps.tenants.models import Tenant
from .models import FeatureModule, PricingPlan

def home(request):
    """
    Public Home Page with Dynamic Data
    """
    # Fetch dynamic content
    features = FeatureModule.objects.all()
    plans = PricingPlan.objects.prefetch_related('features').all()
    
    # Use existing tenant data if available (fallback to empty)
    featured_tenants = Tenant.objects.filter(status='active', is_active=True).order_by('?')[:3]

    context = {
        'features': features,
        'plans': plans,
        'featured_tenants': featured_tenants,
    }
    return render(request, 'public/home.html', context)

from django.core.mail import send_mail
from django.conf import settings

# ... (omitted)

class DemoRequestView(APIView):
    """
    API Endpoint for submitting demo requests
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        from .models import DemoRequest
        
        data = request.data
        try:
            demo_request = DemoRequest.objects.create(
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone', ''),
                institution_name=data.get('institution_name'),
                role=data.get('role', ''),
                message=data.get('message', ''),
                status='new'
            )

            # Send Email Notification
            subject = f"New Demo Request: {demo_request.institution_name}"
            message = f"""
            New Demo Request Received:
            
            Name: {demo_request.name}
            Email: {demo_request.email}
            Phone: {demo_request.phone}
            Institution: {demo_request.institution_name}
            Role: {demo_request.role}
            
            Message:
            {demo_request.message}
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    ['codefyn@gmail.com'],
                    fail_silently=True,
                )
            except Exception as email_error:
                # Log error but don't fail the request
                print(f"Error sending email: {email_error}")

            return Response({'message': 'Request received successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TenantListView(ListView):
    model = Tenant
    template_name = 'public/tenant_list.html'
    context_object_name = 'tenants'
    paginate_by = 12

    def get_queryset(self):
        return Tenant.objects.filter(
            status=Tenant.STATUS_ACTIVE,
            is_active=True
        ).exclude(schema_name='public').order_by('name')

class TenantDetailView(DetailView):
    model = Tenant
    template_name = 'public/tenant_detail.html'
    context_object_name = 'tenant'
    slug_field = 'schema_name'
    slug_url_kwarg = 'schema_name'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.object, 'configuration'):
            context['tenant_config'] = self.object.configuration
        return context
