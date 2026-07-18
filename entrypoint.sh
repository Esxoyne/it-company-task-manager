#!/bin/sh
set -e

python manage.py migrate --noinput

if [ "$DJANGO_DEBUG" = "False" ]; then
    python manage.py collectstatic --noinput
fi

if [ "$LOAD_DEMO_DATA" = "true" ]; then
    if [ -f "demo_data.json" ]; then
        echo "Loading demo data fixture..."
        python manage.py loaddata demo_data.json
    else
        echo "LOAD_DEMO_DATA is true but demo_data.json was not found, skipping."
    fi
fi

if [ -n "$DJANGO_SUPERUSER_NAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    echo "Ensuring superuser '$DJANGO_SUPERUSER_NAME' exists..."
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_NAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_NAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created.')
else:
    print('Superuser already exists, skipping.')
    "
fi

exec "$@"
