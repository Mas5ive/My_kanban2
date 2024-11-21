FROM python:3.10.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.7.5 /uv /uvx /bin/

ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

COPY ./pyproject.toml ./uv.lock ./manage.py /app/
COPY ./my_kanban2 /app/my_kanban2
COPY ./thisapp /app/thisapp
COPY ./user /app/user
COPY ./demo /app/demo

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

CMD ["gunicorn", "my_kanban2.wsgi:application", "--bind", "0.0.0.0:8000"]