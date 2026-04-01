# Nexus — CLI de Bootstrap y Deploy para ERP Nexus

Herramienta CLI para instalar, configurar y desplegar el ERP Nexus en servidores.

No es el ERP — es lo que te ayuda a ponerlo en marcha.

## ¿Qué hace?

- **`nexus init`** — Crea un proyecto ERP nuevo (como `django-admin startproject`)
- **`nexus server`** — Configura y controla el servidor (uvicorn/gunicorn/nginx)
- **`nexus update`** — Actualiza el core ERP a la última versión
- **`nexus doctor`** — Verifica que tu entorno esté listo

## Instalación

```bash
pip install nexus
```

## Flujo típico

```bash
# 1. Crear un proyecto ERP nuevo
nexus init mi-empresa-erp
cd mi-empresa-erp

# 2. Configurar base de datos y migrar
python manage.py migrate
python manage.py createsuperadmin --username admin --email admin@mi.com --password secret

# 3. Configurar servidor de producción
nexus server setup --env production
nexus server start

# 4. Actualizar cuando haya nueva versión
nexus update
```

## Comandos

| Comando | Descripción |
|---|---|
| `nexus init <nombre>` | Crea un proyecto ERP nuevo |
| `nexus server setup` | Genera configs nginx/gunicorn/systemd |
| `nexus server start` | Arranca el servidor |
| `nexus server stop` | Detiene el servidor |
| `nexus server restart` | Reinicia el servidor |
| `nexus update` | Actualiza el core ERP |
| `nexus doctor` | Verifica dependencias del sistema |

## Gestión de módulos

Los módulos se gestionan **dentro del ERP** con Django management commands:

```bash
# Dentro de tu proyecto ERP:
python manage.py install_module ./mi_modulo
python manage.py uninstall_module mi_modulo
python manage.py update_module mi_modulo
python manage.py module list
python manage.py catalog search --category accounting
```

## Crear módulos

Para crear módulos, usa el **SDK Nexus** (dev toolkit):

```bash
pip install sdk-nexus
sdk-nexus create mi_modulo --type=module
sdk-nexus validate ./mi_modulo
sdk-nexus package ./mi_modulo
```

## Licencia

GPL-3.0-or-later
