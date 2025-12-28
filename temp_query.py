import os
import django
from django.conf import settings

# Setup Django (if not using manage.py shell context, but I will run with shell < script)
# Actually better to just run as a standalone script using manage.py shell < script
# OR just standard import inside manage.py shell

from django_tenants.utils import schema_context
from apps.academics.models import AcademicYear

try:
    with schema_context('dps_kolkata'):
        data = list(AcademicYear.objects.values('id', 'name', 'is_current'))
        print("RESULTS_START")
        print(data)
        print("RESULTS_END")
except Exception as e:
    print(f"ERROR: {e}")
