import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import Tenant, Domain

print("Listing Tenants and Domains:")
for t in Tenant.objects.all():
    domains = Domain.objects.filter(tenant=t)
    d_str = ", ".join([d.domain for d in domains])
    print(f"Schema: {t.schema_name} | Name: {t.name} | Domains: {d_str}")
