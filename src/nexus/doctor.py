"""
Comando: nexus doctor

Verifica que el entorno esté listo para ERP Nexus.
"""
import shutil
import subprocess
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


@click.command()
def doctor():
    """Verifica dependencias y configuración del entorno."""
    checks = []
    all_ok = True

    # Python
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info >= (3, 11)
    checks.append(("Python >= 3.11", py_version, py_ok))
    if not py_ok:
        all_ok = False

    # Git
    git_ok = shutil.which("git") is not None
    git_version = ""
    if git_ok:
        r = subprocess.run(["git", "--version"], capture_output=True, text=True)
        git_version = r.stdout.strip()
    checks.append(("Git", git_version or "not found", git_ok))
    if not git_ok:
        all_ok = False

    # uv
    uv_ok = shutil.which("uv") is not None
    uv_version = ""
    if uv_ok:
        r = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        uv_version = r.stdout.strip()
    checks.append(("uv (package manager)", uv_version or "not found", uv_ok))

    # pip
    pip_ok = shutil.which("pip") is not None or shutil.which("pip3") is not None
    checks.append(("pip", "available" if pip_ok else "not found", pip_ok))

    # PostgreSQL (optional)
    pg_ok = shutil.which("psql") is not None
    pg_version = ""
    if pg_ok:
        r = subprocess.run(["psql", "--version"], capture_output=True, text=True)
        pg_version = r.stdout.strip()
    checks.append(("PostgreSQL (optional)", pg_version or "not found", pg_ok))

    # Redis (optional)
    redis_ok = shutil.which("redis-cli") is not None
    checks.append(("Redis (optional)", "available" if redis_ok else "not found", redis_ok))

    # Nginx (optional)
    nginx_ok = shutil.which("nginx") is not None
    checks.append(("Nginx (optional)", "available" if nginx_ok else "not found", nginx_ok))

    # Gunicorn
    try:
        import gunicorn
        gunicorn_ok = True
        gunicorn_version = gunicorn.__version__
    except ImportError:
        gunicorn_ok = False
        gunicorn_version = "not installed"
    checks.append(("Gunicorn (optional)", gunicorn_version, gunicorn_ok))

    # Docker (optional)
    docker_ok = shutil.which("docker") is not None
    checks.append(("Docker (optional)", "available" if docker_ok else "not found", docker_ok))

    # Mostrar resultados
    table = Table(title="🩺 Entorno ERP Nexus", show_header=True, header_style="bold cyan")
    table.add_column("Dependencia")
    table.add_column("Versión/Estado")
    table.add_column("Estado")

    for name, version, ok in checks:
        status = "[green]✅ OK[/green]" if ok else "[yellow]⚠ Falta[/yellow]"
        table.add_row(name, version, status)

    console.print(table)

    if all_ok:
        console.print(Panel.fit(
            "[green]✓ Todas las dependencias requeridas están presentes[/green]",
            title="✅ Entorno OK",
            border_style="green",
        ))
    else:
        console.print(Panel.fit(
            "[yellow]⚠ Faltan dependencias requeridas[/yellow]\n\n"
            "Instala las dependencias marcadas como 'Falta'.\n"
            "Las marcadas como (optional) son recomendadas pero no obligatorias.",
            title="⚠ Revisar Dependencias",
            border_style="yellow",
        ))
