FROM python:3.10.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.5.2 /uv /uvx /bin/
WORKDIR /app

ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen
    
COPY . .