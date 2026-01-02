#!/bin/sh

# Wait for database if DB_HOST is set
if [ "$DB_HOST" = "db" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Run migrations
# echo "Running Migrations..."
# python manage.py migrate --noinput
# We skip auto-migrate for safety in production; admin should run it manually or uncomment.
# For first deployment, it is often safer to run manually.

# Collect static files
# echo "Collecting Static Files..."
# python manage.py collectstatic --noinput

exec "$@"
