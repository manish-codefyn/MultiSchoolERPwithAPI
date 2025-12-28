import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.communications.models import MessageThread, MessageRecipient, Notification
from apps.users.models import User
from django_tenants.utils import tenant_context
from apps.tenants.models import Tenant
from django.contrib.contenttypes.models import ContentType

print("DEBUG: Starting thread repair...")

try:
    # Get the specific tenant
    tenant = Tenant.objects.get(schema_name='dps_kolkata')
    
    with tenant_context(tenant):
        thread_id = "30b99538-1935-4ee9-8262-f2e6e504d0d2"
        try:
            thread = MessageThread.objects.get(id=thread_id)
            print(f"Found thread: {thread.title}")
            
            # Get all active users excluding current participants
            current_participant_ids = thread.participants.values_list('id', flat=True)
            users_to_add = User.objects.filter(is_active=True).exclude(id__in=current_participant_ids)
            
            count = 0
            for user in users_to_add:
                print(f"Adding user: {user.email}")
                thread.participants.add(user)
                count += 1
                
                # Also ensure they have the messages? 
                # Optional, but needed for inbox view usually requires MessageRecipient for the *latest* message often?
                # Actually Thread list view might just need participantship.
                # But Detail view shows messages.
                
            print(f"Successfully added {count} users to the thread.")
            
        except MessageThread.DoesNotExist:
            print(f"Thread {thread_id} does not exist in dps_kolkata.")

except Exception as e:
    print(f"Error: {e}")
