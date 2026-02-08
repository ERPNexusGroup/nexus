#!/usr/bin/env python3
"""
CLI oficial para ERP NEXUS
Minimalista, offline-first, startup < 150ms
"""
# Imports adicionales para comandos
import sys
from datetime import datetime
from pathlib import Path

import click
from nexus import __version__
from nexus.storage.filesystem import FilesystemStorage
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sdk.exceptions import ValidationError
from sdk.validator import ComponentValidator

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


@click.command()
@click.argument("name")
@click.option("--type", "component_type", default="module",
              type=click.Choice(["module", "app"]),
              help="Tipo de componente (default: module)")
@click.option("--path", "-p", default=None,
              help="Ruta de instalación (default: directorio actual)")
@click.option("--minimal", "-m", is_flag=True,
              help="Crear SOLO campos obligatorios (7 campos)")
def create(name: str, component_type: str, path: str, minimal: bool):
    """
    Crea un componente ERP NEXUS con metadata educativa y auto-documentada.

    Ejemplos:
      nexus create hotel_reservations --type=module
      nexus create validation_dni_ec --type=module --minimal
    """
    # Determinar ruta de creación
    base_path = Path(path) if path else Path.cwd()
    component_dir = base_path / name
    component_dir.mkdir(exist_ok=True)

    # Generar contenido educativo de __meta__.py
    if minimal:
        meta_content = _generate_minimal_meta(name, component_type)
    else:
        meta_content = _generate_educational_meta(name, component_type)

    (component_dir / "__meta__.py").write_text(meta_content, encoding="utf-8")

    # Crear estructura básica si no es modo minimal
    if not minimal:
        (component_dir / "__init__.py").write_text(
            f'"""Componente ERP NEXUS: {name}"""\n',
            encoding="utf-8"
        )

        core_dir = component_dir / "core"
        core_dir.mkdir(exist_ok=True)
        (core_dir / "__init__.py").write_text("", encoding="utf-8")
        (core_dir / "models.py").write_text(
            "# Modelos Django - Define tus entidades de negocio aquí\n",
            encoding="utf-8"
        )

    # Validar inmediatamente con SDK (garantiza validez desde el inicio)
    validator = ComponentValidator()
    try:
        metadata = validator.validate_manifest(component_dir)
        console.print(Panel.fit(
            f"[green]✓ Componente creado exitosamente[/green]\n\n"
            f"[bold]Nombre:[/bold] {metadata.technical_name}\n"
            f"[bold]Tipo:[/bold] {metadata.component_type} ({metadata.package_type})\n"
            f"[bold]Versión:[/bold] {metadata.version}\n\n"
            f"[blue]Siguiente paso:[/blue] Edita __meta__.py para personalizar tu componente",
            title="🎉 Componente Listo para Personalizar",
            border_style="green"
        ))
        console.print(f"\n[bold]Ubicación:[/bold] {component_dir.resolve()}")
        console.print(f"[bold]Archivo:[/bold] {component_dir / '__meta__.py'}")

        if not minimal:
            console.print("\n[bold cyan]💡 Consejo para novatos:[/bold cyan]")
            console.print("  1. Abre __meta__.py en tu editor")
            console.print("  2. Lee los comentarios (empiezan con #)")
            console.print("  3. Modifica SOLO los valores entre comillas")
            console.print("  4. Ejecuta: [green]nexus validate {name}[/green] para verificar")

    except ValidationError as e:
        console.print(Panel.fit(
            f"[red]✗ Error de validación:[/red]\n\n{e}\n\n"
            f"[yellow]⚠️ El componente fue creado pero contiene errores.[/yellow]\n"
            f"Corrige los valores en __meta__.py según los comentarios.",
            title="❌ Validación Fallida",
            border_style="red"
        ))
        sys.exit(1)


def _generate_minimal_meta(name: str, component_type: str) -> str:
    """Genera template mínimo con solo los 7 campos obligatorios"""
    return f'''technical_name = "{name}"
display_name = "{name.replace('_', ' ').title()}"
component_type = "{component_type}"
package_type = "extension"
python = ">=3.11"
erp_version = ">=0.1.0"
version = "0.1.0"
'''


def _generate_educational_meta(name: str, component_type: str) -> str:
    """Genera template educativo completo con comentarios explicativos para novatos"""
    return f'''"""
Módulo ERP NEXUS - {name}
=========================

¡Bienvenido! Este archivo define la metadata de tu componente.
NO ejecutes código aquí - solo asigna valores a las variables.

💡 CONSEJO PARA NOVATOS:
  • Edita SOLO los valores entre comillas (ej: "mi_valor")
  • NO elimines las líneas de comentarios (#)
  • Usa comas para separar elementos en listas
  • Guarda el archivo y ejecuta: nexus validate {name}
"""

# ════════════════════════════════════════════════════════════════════════════════
# 🔑 IDENTIDAD DEL COMPONENTE (OBLIGATORIO - 4 campos)
# ════════════════════════════════════════════════════════════════════════════════

# Identificador único interno (snake_case, solo letras minúsculas, números y _)
# ✅ Válido: "hotel_reservations", "validation_dni_ec"
# ❌ Inválido: "HotelReservations", "hotel-reservations"
technical_name = "{name}"

# Nombre visible para usuarios en la interfaz del ERP
# Ej: "Reservas Hoteleras", "Validador Cédula Ecuador"
display_name = "{name.replace('_', ' ').title()}"

# Tipo de componente:
#   "module" → Unidad funcional completa de negocio (ej: reservas, contabilidad)
#   "app"    → Aplicación específica con UI propia (ej: interfaz recepción)
component_type = "{component_type}"

# Rol técnico en el ecosistema:
#   "core"        → Componentes esenciales del núcleo (no recomendado para nuevos devs)
#   "extension"   → ✅ EXTENSIÓN FUNCIONAL (recomendado) - lógica reutilizable sin UI
#   "library"     → Utilidades técnicas puras (ej: generador PDF)
#   "integration" → Conectores con sistemas externos (ej: API Booking.com)
package_type = "extension"

# Área funcional del negocio (opcional, para organización interna)
# Ejemplos: "hospitality", "accounting", "inventory", "hr", "sales"
domain = "custom"


# ════════════════════════════════════════════════════════════════════════════════
# ⚙️ COMPATIBILIDAD DEL SISTEMA (OBLIGATORIO - 2 campos)
# ════════════════════════════════════════════════════════════════════════════════

# Versión mínima de Python requerida
# Formato: ">=X.Y" (ej: ">=3.11", ">=3.12")
python = ">=3.11"

# Versión mínima del core ERP requerida
# Formato semver: ">=X.Y.Z" (ej: ">=0.1.0", ">=1.2.3")
erp_version = ">=0.1.0"

# Restricciones geográficas (opcional)
# "include": ["*"] → Disponible en todos los países
# "include": ["EC", "PE"] → Solo Ecuador y Perú
# "exclude": ["US"] → Todos excepto EE.UU.
geo_restrictions = {{
    "include": ["*"],
    "exclude": []
}}


# ════════════════════════════════════════════════════════════════════════════════
# 📦 DISTRIBUCIÓN Y METADATA (OBLIGATORIO - 1 campo + opcionales)
# ════════════════════════════════════════════════════════════════════════════════

# Versión del componente (Semantic Versioning 2.0.0)
# Formato: "MAJOR.MINOR.PATCH" (ej: "1.2.0", "0.1.0")
# Reglas:
#   MAJOR → Cambios rotos de API
#   MINOR → Nuevas funcionalidades compatibles
#   PATCH → Correcciones de bugs
version = "0.1.0"

# Licencia de distribución (SPDX identifier)
# Ejemplos: "MIT", "GPL-3.0", "Apache-2.0", " proprietary"
license = "MIT"

# Palabras clave para búsqueda (máx. 30 elementos)
# Usa términos en inglés para mejor compatibilidad internacional
keywords = ["erp", "nexus", "{name}"]

# Descripción detallada (mín. 20 caracteres)
# Describe qué hace tu componente y para quién es útil
description = "Componente ERP NEXUS para {name.replace('_', ' ')}"

# Sitio web oficial (opcional)
website = "https://erp-nexus.org"

# Autores y contribuyentes (lista de diccionarios)
# Campos obligatorios: "name", "role"
# Campos opcionales: "email", "website"
authors = [
    {{
        "name": "Tu Nombre",
        "role": "author",       # "author", "maintainer", "contributor"
        "email": "tu@email.com",
        "website": "https://tu-sitio.com"  # opcional
    }}
]


# ════════════════════════════════════════════════════════════════════════════════
# 🔗 DEPENDENCIAS (OPCIONAL - pero crítico para funcionalidad)
# ════════════════════════════════════════════════════════════════════════════════

# Componentes ERP NEXUS requeridos (lista de technical_name)
# Ej: ["validation_dni_ec", "sri_connector"]
# ⚠️ ¡Importante! Estos componentes DEBEN estar instalados antes
depends = []

# Dependencias externas (librerías PyPI y binarios del sistema)
external_dependencies = {{
    "python": [        # Librerías PyPI (especificación pip estándar)
        # Ejemplos válidos:
        # "polars>=0.20.0", 
        # "qrcode>=7.4.0,<8.0.0",
        # "cryptography~=41.0.0"
    ],
    "bin": [           # Binarios requeridos en el sistema operativo
        # Ejemplos:
        # "wkhtmltopdf", 
        # "libreoffice"
    ]
}}

# Dependencias solo para desarrollo/testing (no se instalan en producción)
dev_dependencies = [
    # Ejemplos:
    # "pytest>=8.0.0",
    # "ruff>=0.3.0",
    # "mypy>=1.9.0"
]


# ════════════════════════════════════════════════════════════════════════════════
# 🧠 COMPORTAMIENTO EN EL ERP (OPCIONAL)
# ════════════════════════════════════════════════════════════════════════════════

# ¿Visible en la UI para instalación manual por el usuario?
installable = True

# ¿Instalación automática si sus dependencias están presentes?
#   False → Nunca se instala automáticamente
#   True  → Siempre se instala cuando se instala una dependencia
#   ["dep1", "dep2"] → Solo si ESTAS dependencias específicas están presentes
auto_install = False

# Archivos de datos de demostración (cargados SOLO en modo demo/entrenamiento)
demo_data = [
    # Ejemplos:
    # "demo/reservations.json",
    # "demo/sample_rooms.csv"
]

# Hooks de ciclo de vida (funciones Python a ejecutar en eventos del sistema)
# Formato: "nombre_modulo.ruta.hasta.funcion"
lifecycle = {{
    "pre_install": None,      # Ej: "mi_modulo.hooks.before_install"
    "post_install": None,     # Ej: "mi_modulo.hooks.after_install"
    "post_uninstall": None    # Ej: "mi_modulo.hooks.cleanup"
}}


# ════════════════════════════════════════════════════════════════════════════════
# 🧬 CAMPOS AVANZADOS (OPCIONAL - para casos especiales)
# ════════════════════════════════════════════════════════════════════════════════

# Versión para control de migraciones internas (usado por el sistema)
migration_version = "0.1.0"

# Prioridad de carga en el registry del ERP (0-100)
# Mayor número = se carga antes (útil para extensiones críticas)
load_priority = 50

# Flags de registro: qué elementos registra el módulo en el sistema
registry_flags = {{
    "models": True,    # ¿Tiene modelos de datos? (Django models)
    "api": True,       # ¿Expone API REST?
    "workers": False,  # ¿Usa workers/background tasks?
    "tasks": False     # ¿Tiene tareas programadas?
}}
'''


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--strict", "-s", is_flag=True, help="Modo estricto (warnings como errores)")
def validate(path: str, strict: bool):
    """
    Valida meta.py usando AST parser seguro (sin ejecutar código)
    Ejemplos:
      nexus validate ./hotel_reservations
      nexus validate ./mi_modulo --strict
    """
    component_path = Path(path)

    # Validar que es un directorio con __meta__.py
    if not component_path.is_dir():
        console.print(f"[red]✗ Ruta no es un directorio: {path}[/red]")
        sys.exit(1)

    meta_path = component_path / "__meta__.py"
    if not meta_path.exists():
        console.print(f"[red]✗ No se encontró __meta__.py en {path}[/red]")
        sys.exit(1)

    # Validar con SDK
    validator = ComponentValidator()
    try:
        metadata = validator.validate_manifest(component_path)

        # Mostrar resultado
        console.print(Panel.fit(
            f"[green]✅ VÁLIDO[/green]: {metadata.technical_name} v{metadata.version}",
            title="Validación Exitosa",
            border_style="green"
        ))

        table = Table(show_header=False, box=None)
        table.add_row("[bold]Technical Name[/bold]", metadata.technical_name)
        table.add_row("[bold]Display Name[/bold]", metadata.display_name)
        table.add_row("[bold]Component Type[/bold]", metadata.component_type)
        table.add_row("[bold]Package Type[/bold]", metadata.package_type)
        table.add_row("[bold]Python[/bold]", metadata.python)
        table.add_row("[bold]ERP Version[/bold]", metadata.erp_version)
        console.print(table)

        # Mostrar autores si existen
        if metadata.authors:
            authors = ", ".join([a["name"] for a in metadata.authors])
            console.print(f"\n[bold]Autores:[/bold] {authors}")

        # Mostrar dependencias si existen
        if metadata.depends:
            deps = ", ".join(metadata.depends)
            console.print(f"[bold]Dependencias:[/bold] {deps}")

        console.print("\n[green]✓ El componente es válido y puede instalarse[/green]")

    except ValidationError as e:
        console.print(Panel.fit(
            f"[red]❌ INVÁLIDO[/red]\n\nError: {e}",
            title="Validación Fallida",
            border_style="red"
        ))
        console.print("[yellow]💡 Consejos:[/yellow]")
        console.print("  • Verifica que la versión sea semver válido (ej: 1.2.0)")
        console.print("  • technical_name debe ser snake_case (ej: mi_modulo)")
        console.print("  • component_type debe ser 'module' o 'app'")
        sys.exit(1)


# Registrar comandos en el grupo CLI
cli.add_command(create)
cli.add_command(validate)

if __name__ == "__main__":
    cli()
