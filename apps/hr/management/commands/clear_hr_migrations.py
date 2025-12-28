from django.core.management.base import BaseCommand
from django.db import connection
from django_tenants.utils import schema_context


class Command(BaseCommand):
    help = "Clears migration history for HR app"

    def handle(self, *args, **options):
        tenant_schema = "dps_kolkata"
        self.stdout.write(f"Cleaning migrations for tenant: {tenant_schema}")

        with schema_context(tenant_schema):
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT count(*) FROM django_migrations WHERE app = 'hr'"
                )
                count = cursor.fetchone()[0]
                self.stdout.write(f"Found {count} migration records for 'hr' app.")

                if count > 0:
                    cursor.execute("DELETE FROM django_migrations WHERE app = 'hr'")
                    self.stdout.write("Deleted migration records.")
                else:
                    self.stdout.write("No records to delete.")
