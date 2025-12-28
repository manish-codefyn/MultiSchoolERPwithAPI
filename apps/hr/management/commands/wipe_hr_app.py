from django.core.management.base import BaseCommand
from django.db import connection
from django_tenants.utils import schema_context


class Command(BaseCommand):
    help = "Drops all HR tables and clears migration history for HR app in dps_kolkata"

    def handle(self, *args, **options):
        tenant_schema = "dps_kolkata"
        self.stdout.write(f"Wiping HR tables for tenant: {tenant_schema}")

        # Force the search path on the connection
        with connection.cursor() as cursor:
            cursor.execute(f"SET search_path TO {tenant_schema}")

            # 1. Check and Clear migration history
            cursor.execute("SELECT count(*) FROM django_migrations WHERE app = 'hr'")
            initial_count = cursor.fetchone()[0]
            self.stdout.write(
                f"Found {initial_count} migration records for 'hr' before wipe."
            )

            cursor.execute("DELETE FROM django_migrations WHERE app = 'hr'")
            self.stdout.write("Deleted migration records.")

            cursor.execute("SELECT count(*) FROM django_migrations WHERE app = 'hr'")
            final_count = cursor.fetchone()[0]
            self.stdout.write(f"Remaining migration records: {final_count}")

            # 2. Find and drop tables
            # Note: We must query information_schema.tables with the schema name
            cursor.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_name LIKE 'hr_%%'
            """,
                [tenant_schema],
            )

            tables = [row[0] for row in cursor.fetchall()]

            if tables:
                self.stdout.write(
                    f"Found {len(tables)} tables to drop: {', '.join(tables)}"
                )
                for table in tables:
                    cursor.execute(f'DROP TABLE "{tenant_schema}"."{table}" CASCADE')
                self.stdout.write("All HR tables dropped.")
            else:
                self.stdout.write("No HR tables found.")
