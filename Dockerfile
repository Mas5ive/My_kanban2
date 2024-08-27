FROM python:3.10.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .

RUN pip install --upgrade --no-cache-dir -r requirements.txt

COPY . .