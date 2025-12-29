
from apps.tenants.models import Tenant
from django_tenants.utils import schema_context
from apps.finance.models import FeeStructure
from apps.finance.filters import FeeStructureFilter
from django.http import HttpRequest

try:
    t = Tenant.objects.get(schema_name='dps_kolkata')
    print(f'Tenant: {t.name}')
    with schema_context(t.schema_name):
        count = FeeStructure.objects.count()
        print(f'FeeStructures count: {count}')
        
        if count > 0:
            print(f"Tenant ID: {t.id}")
            
            # Test FilterSet
            print("Testing FilterSet...")
            request = HttpRequest()
            # request.GET is empty by default
            qs = FeeStructure.objects.all()
            f = FeeStructureFilter(request.GET, queryset=qs, request=request)
            print(f"Filter form valid: {f.form.is_valid()}")
            if not f.form.is_valid():
                print(f"Form errors: {f.form.errors}")
            
            print(f"Query: {f.qs.query}")
            print(f"FilterSet.qs.count(): {f.qs.count()}")
            
            if f.qs.count() == 0:
                print("FilterSet HID the record!")
            else:
                 print("FilterSet KEPT the record.")

            print("First few:")
            for fs in FeeStructure.objects.all()[:5]:
                print(f" - {fs.name} (Active: {fs.is_active}, Tenant ID: {fs.tenant_id})")
                if str(fs.tenant_id) != str(t.id):
                    print(f"   MISMATCH! Expected {t.id}")
        
        all_count = FeeStructure.all_objects.count()
        print(f'All Objects count (manager): {all_count}')
except Exception as e:
    print(f"Error: {e}")
