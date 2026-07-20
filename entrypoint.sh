#!/bin/sh
set -e

python manage.py migrate --noinput

if [ "$DJANGO_DEBUG" = "False" ]; then
    python manage.py collectstatic --noinput
fi

if [ "$LOAD_DEMO_DATA" = "true" ]; then
    if [ -f "demo_data.json" ]; then
        ALREADY_LOADED=$(python manage.py shell -c "
from task_manager.models import Worker
print(Worker.objects.filter(username='test').exists())
" | tail -n 1)
        if [ "$ALREADY_LOADED" = "True" ]; then
            echo "Demo data already loaded, skipping."
        else
            echo "Loading demo data fixture..."
            python manage.py loaddata demo_data.json
            
            echo "Resetting DB sequences."
            python manage.py sqlsequencereset task_manager | python manage.py shell -c "
import sys
from django.db import connection
sql = sys.stdin.read()
with connection.cursor() as cursor:
    cursor.execute(sql)
"
        fi
    else
        echo "LOAD_DEMO_DATA is true but demo_data.json was not found, skipping."
    fi
fi

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    echo "Ensuring superuser '$DJANGO_SUPERUSER_USERNAME' exists..."
    python manage.py createsuperuser --noinput 2>/dev/null || echo "Superuser already exists, skipping."
fi

exec "$@"
