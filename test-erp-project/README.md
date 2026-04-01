# test-erp-project

ERP Nexus deployment.

## Quick start

```bash
cd test-erp-project
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
