#!/bin/bash

set -e

python manage.py migrate
python manage.py tailwind install
cd theme/static_src/
npm audit fix
cd ../../
python manage.py tailwind build
python manage.py collectstatic --no-input

uwsgi --socket :8000 --master --enable-threads --module bi.wsgi -i
