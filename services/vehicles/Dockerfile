FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Use system Python from the base image instead of downloading a new one
ENV UV_PYTHON_PREFERENCE=system

# Install dependencies first (cached layer — only re-runs when pyproject.toml/uv.lock change)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy source after dependencies to maximise cache hits
COPY . .

EXPOSE 8001

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
