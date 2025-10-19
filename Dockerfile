FROM python:3.10.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt .

RUN pip install --upgrade --no-cache-dir -r requirements.txt

RUN pip install debugpy

COPY ./my_kanban2 /app/my_kanban2
COPY ./thisapp /app/thisapp
COPY ./user /app/user
COPY ./demo /app/demo
COPY ./manage.py /app/manage.py

CMD ["gunicorn", "my_kanban2.wsgi", "--bind", "0.0.0.0:8000"]