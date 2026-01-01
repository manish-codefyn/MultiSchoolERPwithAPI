import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context

from apps.tenants.models import Tenant
from apps.students.models import Student
from apps.users.models import User

def debug_tenant_counts():
    try:
        tenants = Tenant.objects.exclude(schema_name='public')
        print(f"Found {tenants.count()} tenants.")

        for tenant in tenants:
            print(f"\nChecking tenant: {tenant.name} ({tenant.schema_name})")
            
            # Check User count (Shared Model)
            # Users are filtered by tenant_id in shared schema
            user_count_shared = User.objects.filter(tenant=tenant).count()
            print(f"  User Count (Shared Filter): {user_count_shared}")
            
            with schema_context(tenant.schema_name):
                # Check Student count (Tenant Model)
                student_count = Student.objects.count()
                print(f"  Student Count (Schema Context): {student_count}")
                
                # Check User count inside schema context (should be same if using shared db correctly)
                user_count_context = User.objects.count()
                print(f"  User Count (Schema Context - All): {user_count_context}")

                # List some students to verify existence
                if student_count > 0:
                     print(f"    First 3 students: {list(Student.objects.values_list('first_name', flat=True)[:3])}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_tenant_counts()
