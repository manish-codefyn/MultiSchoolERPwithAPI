import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.tenants.models import Tenant, Domain

def check_domains():
    print("Checking Domains...")
    domains = Domain.objects.all()
    for d in domains:
        print(f"Domain: {d.domain} -> Tenant: {d.tenant.name} ({d.tenant.schema_name})")
    
    print("\nChecking dpskolkata.localhost...")
    exists = Domain.objects.filter(domain='dpskolkata.localhost').exists()
    print(f"Exists: {exists}")

if __name__ == "__main__":
    check_domains()
