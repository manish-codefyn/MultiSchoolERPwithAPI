import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tenants.models import Tenant, Domain
from django_tenants.utils import schema_context
from django.contrib.auth import get_user_model

print("Listing Tenants and Domains:")
has_local_tenant = False
local_domain = "demo.localhost"
demo_schema = "demo"

for t in Tenant.objects.all():
    domains = Domain.objects.filter(tenant=t)
    d_str = ", ".join([d.domain for d in domains])
    print(f"Schema: {t.schema_name} | Domain: {d_str}")
    if any("localhost" in d.domain for d in domains):
        has_local_tenant = True
        local_domain = domains[0].domain
        demo_schema = t.schema_name

if not has_local_tenant:
    print(f"\nNo localhost tenant found. Creating 'demo.localhost' ({demo_schema})...")
    try:
        if not Tenant.objects.filter(schema_name=demo_schema).exists():
           tenant = Tenant(schema_name=demo_schema, name="Demo School", on_trial=True)
           tenant.save()
        else:
           tenant = Tenant.objects.get(schema_name=demo_schema)
        
        if not Domain.objects.filter(domain=local_domain).exists():
            domain = Domain(domain=local_domain, tenant=tenant, is_primary=True)
            domain.save()
        
        print(f"Tenant '{demo_schema}' and Domain '{local_domain}' ready.")
        
        # Create admin user
        with schema_context(demo_schema):
            User = get_user_model()
            email = "admin@demo.com"
            if not User.objects.filter(email=email).exists():
                User.objects.create_superuser(
                    email=email,
                    password="password",
                    first_name="Admin",
                    last_name="User"
                )
                print(f"Superuser '{email}' created with password 'password'")
            else:
                 print(f"Superuser '{email}' already exists.")
    except Exception as e:
        print(f"Error creating demo tenant: {e}")

else:
    print(f"\nUsing existing local tenant: {local_domain} ({demo_schema})")
    # Ensure admin exists
    with schema_context(demo_schema):
        User = get_user_model()
        email = "admin@demo.com"
        # Check if we can find an admin
        if not User.objects.filter(email="admin@demo.com").exists():
             # Try to find ANY superuser
             su = User.objects.filter(is_superuser=True).first()
             if su:
                 print(f"Found existing superuser: {su.email}")
                 su.set_password("password")
                 su.save()
                 print("Password reset to 'password'")
             else:
                User.objects.create_superuser(
                    email=email,
                    password="password",
                    first_name="Admin",
                    last_name="User"
                )
                print(f"Superuser '{email}' created with password 'password'")
        else:
             u = User.objects.get(email=email)
             u.set_password("password")
             u.save()
             print(f"Superuser '{email}' password reset to 'password'")
