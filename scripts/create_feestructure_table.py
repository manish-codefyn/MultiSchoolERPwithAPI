
import os
import sys
import django

# Add project root to path
sys.path.append(r'd:\Python\MultiTenant')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django.setup()

from django.db import connection, transaction
from apps.finance.models import FeeStructure

try:
    with connection.schema_editor() as schema_editor:
        # sql_create_model returns a list of SQL statements and parameters
        # Usually checking the source, it returns list of strings or tuples?
        # In modern Django, it's often executed directly or buffered.
        # But schema_editor.sql_create_model returns the SQL (in older versions) or executes it?
        # create_model(model) executes it.
        
        # To get SQL without executing, use collect_sql=True in SchemaEditor if available or mock.
        # But easier: just execute it! The table is missing, so creating it is what we want!
        print("Attempting to create table...")
        schema_editor.create_model(FeeStructure)
        print("Table created successfully!")

except Exception as e:
    print(f"Error: {e}")
