"""
Nexus — CLI de Bootstrap y Deploy para ERP Nexus.

Comandos:
  nexus init      — Crea un proyecto ERP nuevo
  nexus server    — Configura y controla el servidor
  nexus update    — Actualiza el core ERP
  nexus doctor    — Verifica el entorno
  nexus info      — Información del CLI
"""
import click

from .init import init
from .server import server
from .update import update
from .doctor import doctor
from .info import info


@click.group()
@click.version_option(version=__import__("nexus").__version__, prog_name="nexus")
@click.pass_context
def cli(ctx):
    """
    🚀 nexus — CLI de Bootstrap y Deploy para ERP Nexus

    Herramienta para instalar, configurar y desplegar el ERP Nexus.
    """


cli.add_command(init)
cli.add_command(server)
cli.add_command(update)
cli.add_command(doctor)
cli.add_command(info)


if __name__ == "__main__":
    cli()
