# SubscriptIQ Backend Dockerfile (Powered by uv package manager)
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv from official Astral binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency specification and lockfile first for Docker layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies using uv into /app/.venv
RUN uv sync --frozen --no-dev --no-install-project

# Copy backend application source
COPY . .

# Complete project sync
RUN uv sync --frozen --no-dev

# Add uv virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
