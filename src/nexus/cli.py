#!/usr/bin/env python3
"""
CLI oficial para ERP NEXUS
Minimalista, offline-first, startup < 150ms
"""
# Imports adicionales para comandos
import json
import sys
from datetime import datetime
from pathlib import Path

import click
from nexus import __version__
from nexus.config import load_config
from nexus.storage.filesystem import FilesystemStorage
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from sdk.exceptions import InstallationError, ValidationError
from sdk.dependency.errors import MissingDependencyError, VersionConflictError, CircularDependencyError
from sdk.installer import TransactionalInstaller
from sdk.validator import ComponentValidator
from nexus.catalog import load_catalog_from_source, update_catalog_stub, download_and_extract, CatalogError
from nexus.registry import (
    add_registry,
    get_registry,
    list_registries,
    remove_registry,
    set_default,
    RegistryEntry,
)

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
    cfg = load_config()
    ctx.obj = {"config": cfg}

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
    Valida __meta__.py usando AST parser seguro (sin ejecutar código)

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

        if metadata.authors:
            authors_list = ", ".join([a.name for a in metadata.authors])
            table.add_row("[bold]Autores[/bold]", authors_list)

        console.print(table)

        # Mostrar dependencias si existen
        if metadata.depends:
            deps = ", ".join(metadata.depends)
            console.print(f"\n[bold]Dependencias:[/bold] {deps}")

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


@click.command()
@click.argument("paths", nargs=-1, type=str)
@click.option("--install-path", "-i", default=None,
              help="Ruta base de instalación (default: ~/.nexus/components)")
@click.option("--dry-run", is_flag=True,
              help="Mostrar plan de instalación sin ejecutar cambios")
@click.option("--catalog-source", default=None,
              help="Ruta/URL de catálogo JSON (para items catalog:*)")
@click.option("--registry", "registry_name", default=None,
              help="Registry a usar (por nombre)")
@click.option("--download-dir", default=None,
              help="Directorio de descarga/extracción para paquetes remotos")
@click.option("--package", "package_map", multiple=True,
              help="Mapa de paquete local: name=path (para items catalog:*)")
@click.pass_context
def install(
    ctx,
    paths: tuple[str, ...],
    install_path: str | None,
    dry_run: bool,
    catalog_source: str | None,
    registry_name: str | None,
    download_dir: str | None,
    package_map: tuple[str, ...],
):
    """
    Instala uno o varios componentes con rollback transaccional.
    """
    if not paths:
        console.print("[red]✗ Debes indicar al menos una ruta[/red]")
        sys.exit(1)

    base_path = Path(install_path) if install_path else None
    if base_path is None and isinstance(ctx.obj, dict):
        base_path = ctx.obj["config"].base_path
    storage = FilesystemStorage(base_path=base_path)
    installer = TransactionalInstaller(storage)

    package_lookup: dict[str, Path] = {}
    for item in package_map:
        if "=" not in item:
            console.print(f"[red]✗ Formato inválido en --package:[/red] {item}")
            sys.exit(1)
        name, path = item.split("=", 1)
        package_lookup[name.strip()] = Path(path.strip())

    component_paths = []
    for p in paths:
        if p.startswith("catalog:"):
            technical_name = p.split("catalog:", 1)[1]
            try:
                registry = get_registry(registry_name)
                source = catalog_source or (registry.source if registry else None)
                if not source:
                    raise CatalogError("No hay registry configurado ni --catalog-source.")
                items = load_catalog_from_source(source)
            except CatalogError as e:
                console.print(f"[yellow]{e}[/yellow]")
                sys.exit(1)
            item = next((i for i in items if i.technical_name == technical_name), None)
            if not item:
                console.print(f"[red]✗ No encontrado en catálogo:[/red] {technical_name}")
                sys.exit(1)
            pkg_path = package_lookup.get(technical_name)
            if not pkg_path:
                if item.source:
                    try:
                        pkg_path = download_and_extract(
                            item.source,
                            technical_name,
                            Path(download_dir) if download_dir else None,
                        )
                    except CatalogError as e:
                        console.print(f"[red]✗ {e}[/red]")
                        sys.exit(1)
                else:
                    console.print(
                        f"[red]✗ Falta --package {technical_name}=RUTA[/red]\n"
                        f"Ej: nexus install catalog:{technical_name} "
                        f"--catalog-source C:/ruta/catalog.json "
                        f"--package {technical_name}=C:/ruta/paquete"
                    )
                    sys.exit(1)
            component_paths.append(pkg_path)
        else:
            path_obj = Path(p)
            if not path_obj.exists():
                console.print(f"[red]✗ Ruta no encontrada:[/red] {p}")
                sys.exit(1)
            component_paths.append(path_obj)

    try:
        plan = installer.install_plan(component_paths)

        console.print(f"[bold]Plan:[/bold] {len(plan.install_order)} componente(s)")
        if plan.optional_skipped:
            console.print(f"[yellow]Dependencias opcionales omitidas:[/yellow] {', '.join(plan.optional_skipped)}")

        if dry_run:
            table = Table(title="Plan de Instalación (Dry Run)", show_header=True, header_style="bold cyan")
            table.add_column("Order")
            table.add_column("Component")
            for idx, name in enumerate(plan.install_order, start=1):
                table.add_row(str(idx), name)
            console.print(table)
            return

        results = []
        for name in plan.install_order:
            source_path = plan.paths_by_name.get(name)
            if source_path is None:
                raise InstallationError(f"Plan inválido: no se encontró ruta para '{name}'")
            results.append(installer.install(source_path))

        table = Table(title="Componentes Instalados", show_header=True, header_style="bold cyan")
        table.add_column("Name")
        table.add_column("Version")
        table.add_column("Path")
        for r in results:
            table.add_row(r.name, r.version, str(r.installed_path))
        console.print(table)

    except MissingDependencyError as e:
        console.print(Panel.fit(
            f"[red]❌ Dependencia faltante[/red]\n\n{e}\n\n"
            f"[yellow]Solución:[/yellow] instala primero las dependencias requeridas.\n"
            f"Ej: [green]nexus install /ruta/dep /ruta/componente[/green]\n"
            f"O revisa el plan con [green]--dry-run[/green].",
            title="Dependencias Incompletas",
            border_style="red"
        ))
        sys.exit(1)
    except VersionConflictError as e:
        console.print(Panel.fit(
            f"[red]❌ Conflicto de versión[/red]\n\n{e}\n\n"
            f"[yellow]Solución:[/yellow] actualiza la dependencia a una versión compatible.",
            title="Conflicto de Versiones",
            border_style="red"
        ))
        sys.exit(1)
    except CircularDependencyError as e:
        console.print(Panel.fit(
            f"[red]❌ Dependencia circular[/red]\n\n{e}",
            title="Ciclo Detectado",
            border_style="red"
        ))
        sys.exit(1)
    except InstallationError as e:
        console.print(Panel.fit(
            f"[red]❌ Error de instalación[/red]\n\n{e}",
            title="Instalación Fallida",
            border_style="red"
        ))
        sys.exit(1)


@click.command()
@click.argument("name")
@click.option("--install-path", "-i", default=None,
              help="Ruta base de instalación (default: ~/.nexus/components)")
@click.pass_context
def uninstall(ctx, name: str, install_path: str | None):
    """
    Desinstala un componente por nombre.
    """
    base_path = Path(install_path) if install_path else None
    if base_path is None and isinstance(ctx.obj, dict):
        base_path = ctx.obj["config"].base_path
    storage = FilesystemStorage(base_path=base_path)
    installer = TransactionalInstaller(storage)

    try:
        installer.uninstall(name)
        console.print(f"[green]✓ Desinstalado:[/green] {name}")
    except InstallationError as e:
        console.print(Panel.fit(
            f"[red]❌ Error de desinstalación[/red]\n\n{e}",
            title="Desinstalación Fallida",
            border_style="red"
        ))
        sys.exit(1)


@click.command(name="list")
@click.option("--install-path", "-i", default=None,
              help="Ruta base de instalación (default: ~/.nexus/components)")
@click.pass_context
def list_components(ctx, install_path: str | None):
    """
    Lista componentes instalados desde el registry local.
    """
    base_path = Path(install_path) if install_path else None
    if base_path is None and isinstance(ctx.obj, dict):
        base_path = ctx.obj["config"].base_path
    storage = FilesystemStorage(base_path=base_path)
    items = storage.registry.list()

    if not items:
        console.print("[yellow]No hay componentes instalados.[/yellow]")
        return

    table = Table(title="Componentes Instalados", show_header=True, header_style="bold cyan")
    table.add_column("Name")
    table.add_column("Version")
    table.add_column("Type")
    table.add_column("Installed At")
    table.add_column("Path")

    for item in items:
        table.add_row(
            str(item.get("name", "")),
            str(item.get("version", "")),
            str(item.get("package_type", "")),
            str(item.get("installed_at", "")),
            str(item.get("path", "")),
        )

    console.print(table)


@click.group()
def registry():
    """Operaciones sobre el registry local."""
    pass


@registry.command("export")
@click.option("--output", "-o", default="registry-export.json",
              help="Archivo destino (default: registry-export.json)")
@click.option("--install-path", "-i", default=None,
              help="Ruta base de instalación (default: ~/.nexus/components)")
@click.pass_context
def registry_export(ctx, output: str, install_path: str | None):
    base_path = Path(install_path) if install_path else None
    if base_path is None and isinstance(ctx.obj, dict):
        base_path = ctx.obj["config"].base_path
    storage = FilesystemStorage(base_path=base_path)

    registry_path = storage.registry_path
    if not registry_path.exists():
        console.print("[yellow]No existe registry para exportar.[/yellow]")
        return

    data = registry_path.read_text(encoding="utf-8")
    Path(output).write_text(data, encoding="utf-8")
    console.print(f"[green]✓ Exportado:[/green] {output}")


@registry.command("import")
@click.option("--input", "-i", "input_path", required=True,
              help="Archivo JSON de registry a importar")
@click.option("--overwrite", is_flag=True,
              help="Sobrescribir entradas existentes")
@click.option("--install-path", "-p", default=None,
              help="Ruta base de instalación (default: ~/.nexus/components)")
@click.pass_context
def registry_import(ctx, input_path: str, overwrite: bool, install_path: str | None):
    base_path = Path(install_path) if install_path else None
    if base_path is None and isinstance(ctx.obj, dict):
        base_path = ctx.obj["config"].base_path
    storage = FilesystemStorage(base_path=base_path)

    src = Path(input_path)
    if not src.exists():
        console.print(f"[red]✗ Archivo no encontrado:[/red] {input_path}")
        sys.exit(1)

    try:
        payload = json.loads(src.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        console.print(f"[red]✗ JSON inválido:[/red] {e}")
        sys.exit(1)

    items = []
    if isinstance(payload, dict) and "components" in payload:
        items = list(payload.get("components", {}).values())
    elif isinstance(payload, list):
        items = payload
    else:
        console.print("[red]✗ Formato de registry no soportado[/red]")
        sys.exit(1)

    imported = 0
    skipped = 0
    for item in items:
        name = item.get("name")
        if not name:
            skipped += 1
            continue
        if storage.registry.get(name) and not overwrite:
            skipped += 1
            continue
        storage.registry.register(name, item)
        imported += 1

    console.print(f"[green]✓ Importados:[/green] {imported}")
    if skipped:
        console.print(f"[yellow]Omitidos:[/yellow] {skipped}")


@registry.command("add")
@click.option("--name", required=True)
@click.option("--type", "registry_type", required=True, type=click.Choice(["file", "url", "github"]))
@click.option("--source", required=True)
@click.option("--default", "is_default", is_flag=True)
def registry_add(name: str, registry_type: str, source: str, is_default: bool):
    add_registry(RegistryEntry(name=name, type=registry_type, source=source, is_default=is_default))
    console.print(f"[green]✓ Registry agregado:[/green] {name}")


@registry.command("remove")
@click.option("--name", required=True)
def registry_remove(name: str):
    if remove_registry(name):
        console.print(f"[green]✓ Registry eliminado:[/green] {name}")
    else:
        console.print(f"[yellow]No existe registry:[/yellow] {name}")


@registry.command("list")
def registry_list():
    regs = list_registries()
    if not regs:
        console.print("[yellow]No hay registries configurados.[/yellow]")
        return
    table = Table(title="Registries", show_header=True, header_style="bold cyan")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Source")
    table.add_column("Default")
    for r in regs:
        table.add_row(r.name, r.type, r.source, "yes" if r.is_default else "")
    console.print(table)


@registry.command("set-default")
@click.option("--name", required=True)
def registry_set_default(name: str):
    if set_default(name):
        console.print(f"[green]✓ Default registry:[/green] {name}")
    else:
        console.print(f"[yellow]No existe registry:[/yellow] {name}")


@click.command()
@click.argument("name")
@click.option("--install-path", "-i", default=None,
              help="Ruta base de instalación (default: ~/.nexus/components)")
@click.pass_context
def info(ctx, name: str, install_path: str | None):
    """
    Muestra información detallada de un componente instalado.
    """
    base_path = Path(install_path) if install_path else None
    if base_path is None and isinstance(ctx.obj, dict):
        base_path = ctx.obj["config"].base_path
    storage = FilesystemStorage(base_path=base_path)

    item = storage.registry.get(name)
    if not item:
        console.print(f"[yellow]No se encontró el componente:[/yellow] {name}")
        return

    table = Table(show_header=False, box=None)
    for key in ["name", "version", "component_type", "package_type", "installed_at", "status", "path"]:
        if key in item:
            table.add_row(f"[bold]{key}[/bold]", str(item.get(key, "")))
    console.print(Panel.fit(table, title="Detalles del Componente", border_style="cyan"))


@click.group()
def catalog():
    """Catálogo remoto (stub)."""
    pass


@catalog.command("list")
@click.option("--registry", "registry_name", default=None, help="Registry a usar")
@click.option("--source", default=None, help="Ruta/URL directa (override)")
@click.pass_context
def catalog_list(ctx, registry_name: str | None, source: str | None):
    try:
        registry = get_registry(registry_name)
        src = source or (registry.source if registry else None)
        if not src:
            raise CatalogError("No hay registry configurado ni --source.")
        items = load_catalog_from_source(src)
    except CatalogError as e:
        console.print(f"[yellow]{e}[/yellow]")
        return

    if not items:
        console.print("[yellow]Catálogo vacío.[/yellow]")
        return

    table = Table(title="Catálogo", show_header=True, header_style="bold cyan")
    table.add_column("Technical Name")
    table.add_column("Version")
    table.add_column("Description")
    table.add_column("Source")
    for item in items:
        table.add_row(item.technical_name, item.version, item.description or "", item.source or "")
    console.print(table)


@catalog.command("info")
@click.argument("technical_name")
@click.option("--registry", "registry_name", default=None, help="Registry a usar")
@click.option("--source", default=None, help="Ruta/URL directa (override)")
@click.pass_context
def catalog_info(ctx, technical_name: str, registry_name: str | None, source: str | None):
    try:
        registry = get_registry(registry_name)
        src = source or (registry.source if registry else None)
        if not src:
            raise CatalogError("No hay registry configurado ni --source.")
        items = load_catalog_from_source(src)
    except CatalogError as e:
        console.print(f"[yellow]{e}[/yellow]")
        return

    item = next((i for i in items if i.technical_name == technical_name), None)
    if not item:
        console.print(f"[yellow]No encontrado en catálogo:[/yellow] {technical_name}")
        return

    table = Table(show_header=False, box=None)
    table.add_row("[bold]technical_name[/bold]", item.technical_name)
    table.add_row("[bold]version[/bold]", item.version)
    if item.description:
        table.add_row("[bold]description[/bold]", item.description)
    if item.source:
        table.add_row("[bold]source[/bold]", item.source)
    console.print(Panel.fit(table, title="Catálogo", border_style="cyan"))


@catalog.command("update")
@click.option("--output", "-o", default=None, help="Ruta destino del catálogo JSON")
def catalog_update(output: str | None):
    """
    Actualiza el catálogo remoto (stub).
    """
    path = update_catalog_stub(Path(output) if output else None)
    console.print(f"[green]✓ Catálogo actualizado:[/green] {path}")


cli.add_command(install)
cli.add_command(uninstall)
cli.add_command(list_components)
cli.add_command(info)
cli.add_command(registry)
cli.add_command(catalog)

if __name__ == "__main__":
    cli()
