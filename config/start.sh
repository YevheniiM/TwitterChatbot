#!/bin/bash

# shellcheck disable=SC2164
#python manage.py makemigrations || {
#  echo 'makemigrations has been failed'
#  exit 1
#}

python manage.py migrate || {
  echo 'migration has been failed'
  exit 1
}

exec "$@"
