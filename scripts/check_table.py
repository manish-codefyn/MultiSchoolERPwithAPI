import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def check_table():
    with connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass('public.auth_role_permissions');")
        result = cursor.fetchone()
        print(f"Table 'public.auth_role_permissions' exists: {result[0] is not None}")
        
        # Also check without schema prefix just in case
        cursor.execute("SELECT to_regclass('auth_role_permissions');")
        result_noprefix = cursor.fetchone()
        print(f"Table 'auth_role_permissions' exists (current search path): {result_noprefix[0] is not None}")

if __name__ == "__main__":
    check_table()
