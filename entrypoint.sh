#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."
    while ! python -c "import socket; s = socket.create_connection(('$DB_HOST', '$DB_PORT'))" 2>/dev/null; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Run migrations
# Note: Using migrate_schemas if you are using django-tenants. 
# If standard django, use migrate.
echo "Running migrations..."
python manage.py migrate_schemas --shared
python manage.py migrate_schemas --tenant

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"
