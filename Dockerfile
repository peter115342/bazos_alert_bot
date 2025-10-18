FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock* ./

RUN uv sync --frozen --no-install-project

COPY src/ ./src/

RUN mkdir -p /app/data

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV DB_PATH=/app/data/listings.db

CMD ["uv", "run", "python", "-m", "src.main"]
