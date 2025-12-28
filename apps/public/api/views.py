from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.conf import settings
from apps.tenants.models import Tenant, Domain

class TenantLookupView(APIView):
    """
    Public endpoint to lookup tenant details by schema/code
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        schema = request.query_params.get('schema')
        if not schema:
            return Response(
                {"error": "Schema code is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.db.models import Q
            
            # 1. Try direct match (id, schema, slug)
            tenant = Tenant.objects.filter(
                Q(schema_name__iexact=schema) | 
                Q(slug__iexact=schema)
            ).filter(is_active=True).first()

            # 2. Try domain prefix match
            if not tenant:
                # Matches 'dpskolkata' against 'dpskolkata.localhost' or 'dpskolkata.com'
                domain_match = Domain.objects.filter(
                    domain__istartswith=f"{schema}."
                ).select_related('tenant').first()
                
                if domain_match:
                    tenant = domain_match.tenant

            if not tenant:
                raise Tenant.DoesNotExist

            # Get primary domain
            domain = Domain.objects.filter(tenant=tenant, is_primary=True).first()
            if not domain:
                 domain = Domain.objects.filter(tenant=tenant).first()
            
            domain_url = f"http://{domain.domain}"
            if settings.DEBUG and 'localhost' in domain.domain:
                 # Check if port is needed (dev environment)
                 # Assuming 8000 for now if localhost
                 domain_url = f"http://{domain.domain}:8000"

            return Response({
                "id": str(tenant.id),
                "name": tenant.name,
                "schema_name": tenant.schema_name,
                "domain_url": domain_url,
                "api_url": f"{domain_url}/api/v1/",
                "branding": tenant.branding_info
            })
            
        except Tenant.DoesNotExist:
            return Response(
                {"error": "Institution not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
