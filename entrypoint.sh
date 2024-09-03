#!/bin/sh

if [ "$DEMO_MODE" = "True" ]; then
  echo "DEMO is going"

  python3 manage.py migrate
  python3 manage.py loaddata data.json
  python3 manage.py collectstatic
  
else
  echo "DEMO is skipping"
fi

exec gunicorn my_kanban2.wsgi --bind 0.0.0.0:8000
