import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.communications.models import MessageThread
from apps.users.models import User
from django_tenants.utils import get_tenant_model, tenant_context
from apps.tenants.models import Tenant

print("DEBUG: Starting thread inspection...")

# Try to find the thread in all tenants
TenantModel = get_tenant_model()

try:
    # Iterate over all tenants to find the thread
    for tenant in TenantModel.objects.all():
        with tenant_context(tenant):
            print(f"\nChecking tenant: {tenant.schema_name}")
            try:
                # Try specific ID if you want, or just list all
                thread_id = "30b99538-1935-4ee9-8262-f2e6e504d0d2"
                thread = MessageThread.objects.filter(id=thread_id).first()
                if thread:
                    print(f"FOUND THREAD in schema {tenant.schema_name}!")
                    print(f"ID: {thread.id}")
                    print(f"Title: {thread.title}")
                    print(f"Tenant: {thread.tenant}")
                    print("Participants:")
                    for p in thread.participants.all():
                        print(f" - {p.email} (ID: {p.id})")
                else:
                    print(f"Thread {thread_id} not found in this schema.")
                    
                    # Debug: List recent threads
                    print("Recent threads in this schema:")
                    for t in MessageThread.objects.all()[:5]:
                        print(f" - {t.id} : {t.title} (Participants: {t.participants.count()})")

            except Exception as e:
                print(f"Error checking tenant {tenant.schema_name}: {e}")

except Exception as e:
    print(f"Global error: {e}")
