import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django_tenants.utils import schema_context
from apps.academics.models import SchoolClass, Section, AcademicYear

with schema_context('dps_kolkata'):
    with open('ids.txt', 'w') as f:
        f.write(f"Classes: {list(SchoolClass.objects.values('id', 'name'))}\n")
        f.write(f"Sections: {list(Section.objects.values('id', 'name', 'class_name_id'))}\n")
        f.write(f"Years: {list(AcademicYear.objects.values('id', 'name', 'is_current'))}\n")
