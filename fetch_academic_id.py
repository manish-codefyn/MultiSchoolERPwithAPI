import os, django
import sys

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context
from apps.academics.models import AcademicYear

try:
    with schema_context('dps_kolkata'):
        qs = AcademicYear.objects.filter(is_current=True)
        if not qs.exists():
            print("No current academic year found, listing all...")
            qs = AcademicYear.objects.all()
        
        for item in qs:
            print(f"ID: {item.id}, Name: {item.name}, Current: {item.is_current}")
except Exception as e:
    print(f"ERROR: {e}")
