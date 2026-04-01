FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar uv
RUN pip install uv

# Copiar dependencias
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copiar proyecto
COPY . .

# Collect static
RUN uv run python manage.py collectstatic --noinput || true

EXPOSE 8000
