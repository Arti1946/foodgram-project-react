#!/bin/bash
set -e


python manage.py migrate
python manage.py collectstatic
cp -r /app/collected_static/. /backend_static/static/


exec "$@"