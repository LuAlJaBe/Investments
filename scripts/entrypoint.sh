#!/bin/sh

set -e

python manage.py collectstatic --no-input
python manage.py tailwind build --no-input

uwsgi --socket :8000 --master --enable-threads --module bi.wsgi



