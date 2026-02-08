#!/usr/bin/env python3
"""
CLI oficial para ERP NEXUS
Minimalista, offline-first, startup < 150ms
"""
import click
from rich.console import Console
from rich.panel import Panel
from datetime import datetime
from nexus import __version__

console = Console()


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True
)
@click.version_option(version=__version__, prog_name="nexus")
@click.pass_context
def cli(ctx):
    """
    🚀 nexus - CLI oficial para ERP NEXUS

    Sistema modular de gestión empresarial con enfoque en simplicidad extrema.

    Comandos esenciales:
      create    Crea un componente mínimo válido
      validate  Valida __meta__.py con AST parser seguro
      install   Instala con rollback transaccional garantizado
      uninstall Desinstala limpiamente sin residuos

    Ejemplos:
      nexus create hotel_reservations --type=module
      nexus validate ./mi_modulo
      nexus install ./mi_modulo

    Documentación completa: https://docs.erp-nexus.org/cli
    """
    if ctx.invoked_subcommand is None:
        # Mostrar ayuda inicial si no se especifica comando
        console.print(Panel.fit(
            f"[bold cyan]ERP NEXUS CLI v{__version__}[/bold cyan]\n\n"
            f"🐍 Python: {__import__('sys').version.split()[0]}\n"
            f"📅 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"[bold]¡Listo para crear módulos en < 60 segundos![/bold]",
            title="✨ nexus - Sistema Modular ERP",
            border_style="cyan"
        ))
        console.print("\n[bold]Primeros pasos:[/bold]")
        console.print("  1. Crear módulo:  [green]nexus create mi_modulo --type=module[/green]")
        console.print("  2. Validar:       [green]nexus validate ./mi_modulo[/green]")
        console.print("  3. Instalar:      [green]nexus install ./mi_modulo[/green]")
        console.print("\n[bold]Ver todos los comandos:[/bold] [green]nexus --help[/green]")


if __name__ == "__main__":
    cli()