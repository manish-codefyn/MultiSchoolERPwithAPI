import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

with connection.cursor() as cursor:
    cursor.execute("SET search_path TO public")
    print("Deleting security migrations from django_migrations...")
    cursor.execute("DELETE FROM django_migrations WHERE app='security'")
    print(f"Deleted {cursor.rowcount} rows.")
