FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock* ./
ENV UV_PYTHON_PREFERENCE=system
RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8002
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
