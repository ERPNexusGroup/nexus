<div align="center">

# 🚀 Nexus

**CLI de Bootstrap y Deploy para ERP Nexus**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](CHANGELOG.md)

[Instalación](#instalación) • [Uso rápido](#uso-rápido) • [Comandos](#comandos) • [Producción](#producción)

</div>

---

## ¿Qué es?

Nexus es la herramienta CLI para **instalar, configurar y desplegar** el ERP Nexus. Piensa en ella como el `bench` de Frappe o `odoo-bin` de Odoo.

> **Nota:** Nexus **no gestiona módulos**. Para instalar/desinstalar módulos, usa `manage.py install_module` dentro del ERP. Para crear módulos, usa `sdk-nexus`.

## Instalación

```bash
pip install nexus
```

## Uso rápido

```bash
# 1. Crear un proyecto ERP nuevo
nexus init mi-erp --with-docker --with-git

# 2. Configurar
cd mi-erp
cp .env.example .env
uv sync

# 3. Verificar entorno
nexus doctor

# 4. Arrancar en desarrollo
uv run python manage.py migrate
uv run python manage.py bootstrap_superadmin --username admin --email admin@local --password changeme
uv run python manage.py runserver

# 5. Configurar para producción
nexus server setup --domain erp.miempresa.com
nexus server start
```

## Comandos

| Comando | Descripción |
|---------|-------------|
| `nexus init` | Crea un proyecto ERP nuevo |
| `nexus server` | Configura y controla el servidor |
| `nexus update` | Actualiza el core ERP |
| `nexus doctor` | Verifica el entorno |
| `nexus info` | Estado del proyecto |

### init

Crea un proyecto ERP completo con toda la estructura necesaria.

```bash
nexus init <nombre> [opciones]

Opciones:
  --with-docker   Generar docker-compose.yml y Dockerfile
  --with-git      Inicializar repositorio git
```

Genera:
```
mi-erp/
├── manage.py             # Django management CLI
├── pyproject.toml        # Dependencias
├── .env.example          # Variables de entorno
├── .gitignore
├── README.md
├── modules/              # Directorio de módulos
├── staticfiles/
├── media/
├── docker-compose.yml    # (con --with-docker)
└── Dockerfile            # (con --with-docker)
```

### server

```bash
nexus server setup    # Genera configs (nginx, gunicorn, systemd)
nexus server start    # Arranca el servidor
nexus server stop     # Detiene el servidor
nexus server restart  # Reinicia
nexus server status   # Estado del servidor
```

#### server setup

Genera configuración de producción:

```bash
nexus server setup --domain erp.miempresa.com --port 8000 --workers 4
```

Archivos generados:
```
config/
├── nginx.conf              # Config nginx (reverse proxy + SSL)
└── mi_erp.service          # Systemd service
gunicorn.conf.py            # Gunicorn config (workers, logging)
```

#### Activar en producción

```bash
# 1. Nginx
sudo cp config/nginx.conf /etc/nginx/sites-available/mi-erp
sudo ln -s /etc/nginx/sites-available/mi-erp /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 2. Systemd
sudo cp config/mi_erp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mi_erp
sudo systemctl start mi_erp

# 3. Verificar
sudo systemctl status mi_erp
nexus server status
```

### update

Actualiza el core ERP a la última versión.

```bash
nexus update --check   # Solo verificar versión disponible
nexus update           # Actualizar (migrate + collectstatic)
nexus update --yes     # Actualizar sin confirmar
```

### doctor

Verifica que el entorno tenga las dependencias necesarias.

```bash
nexus doctor
```

```
🩺 Entorno ERP Nexus
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Dependencia           ┃ Versión/Estado            ┃ Estado  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ Python >= 3.11        │ 3.11.2                    │ ✅ OK   │
│ Git                   │ git version 2.39.5        │ ✅ OK   │
│ uv (package manager)  │ uv 0.11.2                 │ ✅ OK   │
│ PostgreSQL (optional) │ available                 │ ✅ OK   │
│ Redis (optional)      │ available                 │ ✅ OK   │
│ Nginx (optional)      │ available                 │ ✅ OK   │
└───────────────────────┴───────────────────────────┴─────────┘
```

### info

Muestra estado del proyecto actual.

```bash
cd mi-erp
nexus info
```

## Producción

### Stack recomendado

```
Internet
   │
   ▼
┌──────────┐
│  Nginx   │  ← SSL termination, static files, reverse proxy
└────┬─────┘
     │
┌────▼─────┐
│ Gunicorn │  ← ASGI workers (uvicorn)
│ +Uvicorn │
└────┬─────┘
     │
┌────▼──────────┐
│  PostgreSQL   │  ← Base de datos
└────┬──────────┘
     │
┌────▼──────────┐
│    Redis      │  ← Cache + Celery broker
└───────────────┘
```

### Variables de entorno

```bash
# Django
DJANGO_SECRET_KEY=tu-clave-secreta-aqui
DJANGO_SETTINGS_MODULE=erp_nexus.settings.production
DJANGO_ALLOWED_HOSTS=erp.miempresa.com

# Database
POSTGRES_DB=erp_nexus
POSTGRES_USER=erp_nexus
POSTGRES_PASSWORD=changeme
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
```

### Docker

```bash
# Iniciar todo
docker-compose up -d

# Ver logs
docker-compose logs -f web

# Ejecutar comandos
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py install_module ./mi_modulo
```

## Gestión de módulos

Los módulos se gestionan **dentro del ERP**, no con Nexus:

```bash
# Dentro de tu proyecto ERP:
cd mi-erp

# Instalar módulo
uv run python manage.py install_module ./accounting_basic
uv run python manage.py install_module --git https://github.com/org/module
uv run python manage.py install_module --package module-0.1.0.npkg

# Gestionar
uv run python manage.py module list
uv run python manage.py module info accounting_basic
uv run python manage.py module sync

# Desinstalar
uv run python manage.py uninstall_module accounting_basic
```

## Crear módulos

Para crear módulos, usa **SDK Nexus**:

```bash
pip install sdk-nexus

# Crear
sdk-nexus create mi_modulo --type=module

# Validar
sdk-nexus validate ./mi_modulo

# Empaquetar
sdk-nexus package ./mi_modulo

# Instalar en el ERP
cd mi-erp
manage.py install_module --package ./dist/mi_modulo-0.1.0.npkg
```

## Ecosistema ERP Nexus

```
┌─────────────────────────────────────────────────┐
│  sdk-nexus  →  Dev Toolkit                      │
│  Crear, validar, empaquetar módulos             │
├─────────────────────────────────────────────────┤
│  nexus (CLI)  →  Bootstrap/Deploy (este repo)   │
│  init / server / update / doctor                │
├─────────────────────────────────────────────────┤
│  erp-nexus  →  ERP Core (Django)                │
│  API, Events, Management Commands               │
├─────────────────────────────────────────────────┤
│  Módulos  →  accounting, invoicing, inventory...│
└─────────────────────────────────────────────────┘
```

## Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para guías de contribución, git flow y convenciones.

## Licencia

GPL-3.0-or-later — Ver [LICENSE](LICENSE)
