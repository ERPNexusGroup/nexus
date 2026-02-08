"""
Implementación minimalista de StorageBackend para CLI
Usa filesystem local + JSON registry (sin base de datos)
"""
from pathlib import Path
from typing import Optional
from sdk.contracts import StorageBackend
from sdk.registry import ComponentRegistry
import shutil


class FilesystemStorage(StorageBackend):
    """
    Implementación de StorageBackend usando filesystem local
    
    Características:
    - Zero dependencias externas (solo stdlib)
    - 100% offline
    - Registry en JSON (registry.json)
    - Rollback automático vía eliminación recursiva
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.home() / ".nexus" / "components"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.registry_path = self.base_path / "registry.json"
        self.registry = ComponentRegistry(self.registry_path)
    
    def copy_files(self, source: Path, destination: Path) -> None:
        """Copia recursiva con shutil (máxima eficiencia)"""
        if not source.exists():
            raise FileNotFoundError(f"Origen no encontrado: {source}")
        
        if destination.exists():
            shutil.rmtree(destination)
        
        shutil.copytree(source, destination)
    
    def remove_files(self, path: Path) -> None:
        """Elimina recursivamente (idempotente)"""
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    
    def register_component(self, path: Path, manifest: dict) -> None:
        """Registra en JSON registry"""
        # Extraer campos esenciales del manifest
        technical_name = manifest.get("technical_name", "unknown")
        
        self.registry.register(technical_name, {
            "name": technical_name,
            "version": manifest.get("version", "0.0.0"),
            "path": str(path.resolve()),
            "component_type": manifest.get("component_type", "module"),
            "package_type": manifest.get("package_type", "extension"),
            "installed_at": "2024-05-22T10:00:00",
            "status": "active"
        })
    
    def unregister_component(self, name: str) -> None:
        """Elimina del registry"""
        self.registry.unregister(name)
    
    def resolve_dependency(self, name: str, version_spec: str) -> Optional[Path]:
        """Resuelve desde filesystem local (offline-first)"""
        candidate = self.base_path / name
        return candidate if candidate.exists() else None
    
    def get_default_install_path(self, component_name: str) -> Path:
        """Ruta por defecto de instalación"""
        return self.base_path / component_name
