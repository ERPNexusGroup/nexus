"""
Comando: nexus update

Actualiza el core ERP Nexus a la última versión.
"""
import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.command()
@click.option("--check", is_flag=True, help="Solo verificar sin actualizar")
@click.option("--yes", "-y", is_flag=True, help="Confirmar automáticamente")
def update(check: bool, yes: bool):
    """
    Actualiza el core ERP Nexus.

    Ejemplos:

      nexus update --check    # Verificar versión disponible

      nexus update            # Actualizar
    """
    project_dir = Path.cwd()

    if not (project_dir / "manage.py").exists():
        console.print("[red]✗ No se encontró manage.py — ¿estás en un proyecto ERP Nexus?[/red]")
        sys.exit(1)

    # Verificar versión actual
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "erp-nexus"],
            capture_output=True, text=True,
        )
        current_version = "unknown"
        for line in result.stdout.split("\n"):
            if line.startswith("Version:"):
                current_version = line.split(":")[1].strip()
                break
    except Exception:
        current_version = "unknown"

    console.print(f"📦 Versión actual: [bold]{current_version}[/bold]")

    if check:
        # Solo verificar
        result = subprocess.run(
            [sys.executable, "-m", "pip", "index", "versions", "erp-nexus"],
            capture_output=True, text=True,
        )
        console.print(f"   Última versión disponible: {result.stdout.strip()[:100]}")
        return

    # Confirmar
    if not yes:
        click.confirm("¿Actualizar erp-nexus?", abort=True)

    console.print("📥 Actualizando erp-nexus...")

    # 1. Actualizar paquete
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "erp-nexus"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        console.print(f"[red]✗ Error actualizando: {result.stderr}[/red]")
        sys.exit(1)
    console.print("   ✅ Paquete actualizado")

    # 2. Ejecutar migraciones
    console.print("🔄 Ejecutando migraciones...")
    result = subprocess.run(
        [sys.executable, "manage.py", "migrate"],
        capture_output=True, text=True, cwd=str(project_dir),
    )
    if result.returncode == 0:
        console.print("   ✅ Migraciones aplicadas")
    else:
        console.print(f"[yellow]⚠ Migraciones: {result.stderr}[/yellow]")

    # 3. Collect static
    console.print("📁 Recolectando archivos estáticos...")
    subprocess.run(
        [sys.executable, "manage.py", "collectstatic", "--noinput"],
        capture_output=True, text=True, cwd=str(project_dir),
    )
    console.print("   ✅ Static files actualizados")

    console.print(Panel.fit(
        f"[green]✓ Actualización completada[/green]\n\n"
        f"[bold]Antes:[/bold] {current_version}\n\n"
        f"[bold]Siguiente:[/bold] nexus server restart",
        title="🔄 ERP Nexus Actualizado",
        border_style="green",
    ))
