#!/bin/bash

echo "Waiting for mysql..."
while ! nc -z database 3306; do
  sleep 0.1
done
echo "mysql is ready..."

# shellcheck disable=SC2164
cd /proj/src/
#python manage.py makemigrations || {
#  echo 'makemigrations has been failed'
#  exit 1
#}
#
#python manage.py migrate || {
#  echo 'migration has been failed'
#  exit 1
#}
#python manage.py collectstatic --no-input || {
#  echo 'static collection has been failed'
#  exit 1
#}
python manage.py runserver 0.0.0.0:8000 || {
  echo 'server start has been failed'
  exit 1
}

exec "$@"
