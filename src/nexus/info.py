"""
Comando: nexus info

Muestra información del CLI y del proyecto actual.
"""
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__

console = Console()


@click.command()
def info():
    """Muestra información del CLI y del proyecto actual."""
    project_dir = Path.cwd()
    is_project = (project_dir / "manage.py").exists()

    # Info del CLI
    table = Table(show_header=False, box=None)
    table.add_row("[bold]Nexus CLI[/bold]", __version__)
    table.add_row("[bold]Directorio[/bold]", str(project_dir))
    table.add_row("[bold]Proyecto ERP[/bold]", "✅ Sí" if is_project else "❌ No")

    if is_project:
        # Leer pyproject.toml para info del proyecto
        pyproject = project_dir / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text()
            for line in content.split("\n"):
                if line.startswith("version"):
                    version = line.split("=")[1].strip().strip('"')
                    table.add_row("[bold]Versión proyecto[/bold]", version)
                    break

        # Verificar .env
        env_file = project_dir / ".env"
        table.add_row("[bold].env[/bold]", "✅ Existe" if env_file.exists() else "⚠ No encontrado")

        # Verificar DB
        db_file = project_dir / "db.sqlite3"
        table.add_row("[bold]SQLite DB[/bold]", "✅" if db_file.exists() else "—")

        # Verificar módulos
        modules_dir = project_dir / "modules"
        if modules_dir.exists():
            modules = [d for d in modules_dir.iterdir() if d.is_dir() and (d / "__meta__.py").exists()]
            table.add_row("[bold]Módulos[/bold]", f"{len(modules)} instalados")
        else:
            table.add_row("[bold]Módulos[/bold]", "0 (directorio no existe)")

    console.print(Panel.fit(
        table,
        title="🚀 Nexus — Info",
        border_style="cyan",
    ))

    if not is_project:
        console.print("\n[blue]¿Quieres crear un proyecto?[/blue]")
        console.print("  nexus init mi-erp")
