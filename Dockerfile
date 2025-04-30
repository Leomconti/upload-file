FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

ENV PYTHONUNBUFFERED=1

COPY uv.lock pyproject.toml /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

COPY . /app/

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
