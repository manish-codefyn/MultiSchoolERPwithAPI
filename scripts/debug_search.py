import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.students.models import Student
from apps.tenants.models import Tenant
from django_tenants.utils import schema_context

try:
    t = Tenant.objects.get(schema_name='dps_kolkata')
    print(f'Tenant: {t.name}')
    with schema_context(t.schema_name):
        students = list(Student.objects.all().values_list('first_name', 'last_name', 'admission_number'))
        print(f"Total Students: {len(students)}")
        for s in students:
            print(s)
except Exception as e:
    print(e)
