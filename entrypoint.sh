#!/bin/sh

if [ "$MIGRATION" = "True" ]; then
  echo "MIGRATION is going"
  python3 manage.py migrate
fi

if [ "$DEBUG" = "True" ]; then
  echo "Run your debug client now!" 
  exec python3 -m debugpy --wait-for-client --listen 0.0.0.0:5678 manage.py runserver 0.0.0.0:8000
else
  python3 manage.py collectstatic
  exec gunicorn my_kanban2.wsgi --bind 0.0.0.0:8000
fi