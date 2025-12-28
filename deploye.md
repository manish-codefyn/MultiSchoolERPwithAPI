
docker-compose exec db sh -c 'psql -U "$DB_USER" -d "$DB_NAME"'

🟦 STEP 6 — Create PostgreSQL Database (Correct Script)
psql -U postgres

Create database + user
CREATE DATABASE eduerp_v6;
CREATE USER codefyn WITH PASSWORD 'Jaimaa@007';

ALTER ROLE codefyn SET client_encoding TO 'utf8';
ALTER ROLE codefyn SET default_transaction_isolation TO 'read committed';
ALTER ROLE codefyn SET timezone TO 'Asia/Kolkata';

GRANT ALL PRIVILEGES ON DATABASE eduerp_v6 TO codefyn;
\q

docker-compose exec db sh -c 'psql -U "$DB_USER" -d "$DB_NAME"'


eduerp_v6=# CREATE USER codefyn WITH PASSWORD 'Jaimaa@007';
ERROR:  role "codefyn" already exists
eduerp_v6=# ALTER ROLE codefyn SET client_encoding TO 'utf8';
ALTER ROLE
eduerp_v6=# ALTER ROLE codefyn SET default_transaction_isolation TO 'read
eduerp_v6'# ALTER ROLE codefyn SET timezone TO 'Asia/Kolkata';
eduerp_v6'#
eduerp_v6'# GRANT ALL PRIVILEGES ON DATABASE eduerp_v6 TO codefyn;
eduerp_v6'# CREATE SCHEMA IF NOT EXISTS public;
eduerp_v6'# ALTER SCHEMA public OWNER TO codefyn;
eduerp_v6'# GRANT ALL ON SCHEMA public TO codefyn;
eduerp_v6'# ALTER ROLE codefyn SET search_path = public;
eduerp_v6'# ALTER DATABASE eduerp_v6 SET search_path TO public;
eduerp_v6'# \q
Use control-D to quit.
eduerp_v6'#
\q

1>
tenant = Tenant.objects.get(schema_name="dps_kolkata")

Domain.objects.create(
    domain="dps.demo2.codefyn.com",
    tenant=tenant,
    is_primary=True
)


2>
from apps.tenants.models import Domain, Tenant

tenant = Tenant.objects.get(schema_name="dps_kolkata")

Domain.objects.create(
    domain="dps.demo2.codefyn.com",
    tenant=tenant,
    is_primary=True,
    is_verified=True
)

✅ aapanel → Website → Reverse Proxy
Proxy Settings
Field	Value
Target URL	http://127.0.0.1:8700
Sent Domain	$host
Proxy directory	/
Cache	OFF
Rewrite	empty


http://demo2.codefyn.com
http://dps.demo2.codefyn.com
http://sanskriti.demo2.codefyn.com

python manage.py shell

from apps.tenants.models import Domain
Domain.objects.select_related("tenant").values("domain","tenant__schema_name")


# 👍 — this is one of the most confusing but important production concepts.

Short answer first:

✅ Gunicorn should bind to 127.0.0.1:8700, not the public IP, even if your server IP is 103.180.236.86.

Below is a clear explanation + correct setup for aaPanel so you understand why.

🔑 Key Concept (Very Important)

There are two layers:

1️⃣ Internal app server (Gunicorn / Django)

Runs inside the server

Should NOT be exposed directly to the internet

Listens on 127.0.0.1:8700

2️⃣ Web server / Reverse proxy (Nginx via aaPanel)

Public-facing

Listens on:

http://103.180.236.86
http://demo2.codefyn.com


Forwards requests → 127.0.0.1:8700

✅ Correct Architecture
Internet
   |
   |  (HTTP / HTTPS)
   v
Nginx (aaPanel)
   ├── demo2.codefyn.com
   ├── *.demo2.codefyn.com
   |
   └── proxy_pass → http://127.0.0.1:8700
                          |
                          v
                     Gunicorn
                     Django

✅ Why NOT use 103.180.236.86:8700 for Gunicorn?
❌ Problems if you bind Gunicorn to public IP
gunicorn --bind 103.180.236.86:8700


This causes:

❌ Port exposed to the internet
❌ Security risk
❌ Firewall issues
❌ Nginx proxy conflicts
❌ Harder SSL handling
❌ Not recommended in production

✅ Correct Gunicorn Command (RECOMMENDED)
gunicorn config.wsgi:application \
  --bind 127.0.0.1:8700 \
  --workers 3 \
  --timeout 120


This means:

✔ Only accessible locally
✔ aaPanel → Nginx handles public traffic
✔ SSL works
✔ Subdomains work
✔ Safer

✅ aaPanel Proxy Configuration (IMPORTANT)

Inside Website → demo2.codefyn.com → Reverse Proxy

Field	Value
Proxy Name	django
Proxy Path	/
Target URL	http://127.0.0.1:8700
Sent Domain	$host
Cache	OFF

This allows:

demo2.codefyn.com        → Django
dps.demo2.codefyn.com    → Django
sanskriti.demo2.codefyn.com → Django


All passed via $host.

✅ Your Django settings are already correct

You already have:

ALLOWED_HOSTS = [
    "103.180.236.86",
    "demo2.codefyn.com",
    ".demo2.codefyn.com",
]


✅ Perfect
Django uses Host header, not port binding.

✅ How Django knows tenant?

django-tenants reads:

Host: dps.demo2.codefyn.com


Then it matches:

Domain(domain="dps.demo2.codefyn.com")


So tenant routing works automatically.

🔥 Summary (simple words)
Thing	Correct Value
Public URL	http://103.180.236.86
Domain	demo2.codefyn.com
Subdomain tenants	*.demo2.codefyn.com
Gunicorn bind	127.0.0.1:8700
aaPanel proxy →	127.0.0.1:8700
Django ALLOWED_HOSTS	include domain + subdomains
Domain mapping	in Domain table


  # ----------------------------------
    # Django static files
    # ----------------------------------
    location /static/ {
        alias /www/wwwroot/demo2.codefyn.com/staticfiles/;
        expires 30d;
        access_log off;
    }

    location /media/ {
        alias /www/wwwroot/demo2.codefyn.com/media/;
        expires 30d;
        access_log off;
    }

URL	Result
https://demo2.codefyn.com
	public schema
https://dpskolkata.demo2.codefyn.com
	DPS tenant
https://sanskritiahmedabad.demo2.codefyn.com
	Sanskriti tenant
http://127.0.0.1:8700
	internal only
http://103.180.236.86
	redirected to HTTPS


c1
python manage.py collectstatic
python manage.py migrate_schemas --schema=public

python manage.py migrate_schemas
python manage.py load_tenants
python manage.py create_tenant_superuser --tenant=dps_kolkata --email=admin@dpskolkata.com --password=admin123
python manage.py create_tenant_superuser --tenant=sanskriti_ahmedabad --email=admin@sanskriti.com --password=admin123
python manage.py create_tenant_superuser --tenant=public --email=admin@public.com --password=admin123


# Initialize permissions
python manage.py assign_roles
python manage.py init_permissions
python manage.py populate_public_data

# Also populate public schema with reference data
python manage.py load_academics_dummy --public-schema

python manage.py load_admission_dummy --tenant dps_kolkata
python manage.py load_students_dummy --tenant dps_kolkata --count 50

