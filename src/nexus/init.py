"""
Comando: nexus init <nombre>

Crea un proyecto ERP Nexus nuevo (como django-admin startproject).
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

console = Console()

# Templates de archivos del proyecto
PROJECT_TEMPLATE = """#!/usr/bin/env python3
import os
import sys
from pathlib import Path


def main() -> None:
    # Añadir modules/ al path para imports dinámicos
    BASE_DIR = Path(__file__).resolve().parent
    modules_dir = BASE_DIR / "modules"
    if str(modules_dir) not in sys.path:
        sys.path.insert(0, str(modules_dir))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erp_nexus.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
"""

ENV_TEMPLATE = """# ERP Nexus — Environment Configuration
# Copy this to .env and customize

# Django
DJANGO_SECRET_KEY=change-me-to-a-random-string
DJANGO_SETTINGS_MODULE=erp_nexus.settings.production
DJANGO_ALLOWED_HOSTS=localhost,your-domain.com

# Database (PostgreSQL)
POSTGRES_DB=erp_nexus
POSTGRES_USER=erp_nexus
POSTGRES_PASSWORD=changeme
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
"""

DOCKER_COMPOSE_TEMPLATE = """version: "3.9"

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: erp_nexus
      POSTGRES_USER: erp_nexus
      POSTGRES_PASSWORD: changeme
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  web:
    build: .
    command: >
      gunicorn erp_nexus.asgi:application
        -w 4
        -k uvicorn.workers.UvicornWorker
        --bind 0.0.0.0:8000
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - db
      - redis
    volumes:
      - ./modules:/app/modules
      - ./staticfiles:/app/staticfiles

  celery:
    build: .
    command: celery -A erp_nexus worker -l info
    env_file: .env
    depends_on:
      - db
      - redis

volumes:
  pgdata:
"""

DOCKERFILE_TEMPLATE = """FROM python:3.11-slim

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
"""

GITIGNORE_TEMPLATE = """# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/

# Django
*.sqlite3
db.sqlite3
staticfiles/
media/

# Environment
.env
.env.local

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# ERP Nexus
modules/installed.json
"""

PYPROJECT_TEMPLATE = """[project]
name = "{name}"
version = "0.1.0"
description = "ERP Nexus deployment — {name}"
requires-python = ">=3.11"
dependencies = [
    "erp-nexus>=0.2.0",
    "django>=5.0,<5.1",
    "django-ninja>=1.0.0",
    "django-jazzmin>=3.0.0",
    "uvicorn>=0.29.0",
    "pydantic>=2.6.0",
    "semantic-version>=2.10.0",
]

[project.optional-dependencies]
production = [
    "gunicorn>=22.0.0",
    "psycopg[binary]>=3.1.0",
    "redis>=5.0.0",
    "celery[redis]>=5.4.0",
]
dev = [
    "pytest>=8.0.0",
    "pytest-django>=4.8.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "erp_nexus.settings.development"
pythonpath = ["."]
"""


@click.command()
@click.argument("name")
@click.option(
    "--with-docker", is_flag=True,
    help="Generar docker-compose.yml y Dockerfile",
)
@click.option(
    "--with-git", is_flag=True,
    help="Inicializar repositorio git",
)
def init(name: str, with_docker: bool, with_git: bool):
    """
    Crea un proyecto ERP Nexus nuevo.

    Ejemplos:

      nexus init mi-erp

      nexus init mi-erp --with-docker --with-git
    """
    project_dir = Path.cwd() / name

    if project_dir.exists():
        console.print(f"[red]✗ Ya existe: {project_dir}[/red]")
        sys.exit(1)

    console.print(f"🚀 Creando proyecto: {name}")

    # Crear directorios
    dirs = [
        project_dir,
        project_dir / "modules",
        project_dir / "staticfiles",
        project_dir / "media",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # manage.py
    (project_dir / "manage.py").write_text(PROJECT_TEMPLATE)
    (project_dir / "manage.py").chmod(0o755)
    console.print("   ✅ manage.py")

    # pyproject.toml
    (project_dir / "pyproject.toml").write_text(
        PYPROJECT_TEMPLATE.format(name=name)
    )
    console.print("   ✅ pyproject.toml")

    # .env.example
    (project_dir / ".env.example").write_text(ENV_TEMPLATE)
    console.print("   ✅ .env.example")

    # .gitignore
    (project_dir / ".gitignore").write_text(GITIGNORE_TEMPLATE)
    console.print("   ✅ .gitignore")

    # README
    readme = f"""# {name}

ERP Nexus deployment.

## Quick start

```bash
cd {name}
uv sync
cp .env.example .env  # Edita con tus valores
uv run python manage.py migrate
uv run python manage.py bootstrap_superadmin --username admin --email admin@local --password changeme
uv run python manage.py runserver
```

## Install modules

```bash
uv run python manage.py install_module ./path/to/module
uv run python manage.py module list
```

## Production

```bash
nexus server setup --env production
nexus server start
```
"""
    (project_dir / "README.md").write_text(readme)
    console.print("   ✅ README.md")

    # Docker files
    if with_docker:
        (project_dir / "docker-compose.yml").write_text(DOCKER_COMPOSE_TEMPLATE)
        console.print("   ✅ docker-compose.yml")
        (project_dir / "Dockerfile").write_text(DOCKERFILE_TEMPLATE)
        console.print("   ✅ Dockerfile")

    # Git init
    if with_git:
        subprocess.run(["git", "init"], cwd=project_dir, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=project_dir, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"Initial commit — {name} ERP Nexus project"],
            cwd=project_dir, capture_output=True,
        )
        console.print("   ✅ git init + initial commit")

    console.print(Panel.fit(
        f"[green]✓ Proyecto creado exitosamente[/green]\n\n"
        f"[bold]Directorio:[/bold] {project_dir}\n\n"
        f"[bold]Siguientes pasos:[/bold]\n"
        f"  1. cd {name}\n"
        f"  2. cp .env.example .env (editar valores)\n"
        f"  3. uv sync\n"
        f"  4. uv run python manage.py migrate\n"
        f"  5. uv run python manage.py bootstrap_superadmin "
        f"--username admin --email admin@local --password changeme\n"
        f"  6. uv run python manage.py runserver\n\n"
        f"[dim]Instalar módulos: manage.py install_module <path>[/dim]",
        title="🎉 Proyecto Listo",
        border_style="green",
    ))
