"""
Configuración del proyecto ERP Nexus.

Lee y escribe .env y config local del proyecto.
"""
import os
from pathlib import Path
from typing import Optional


class ProjectConfig:
    """
    Configuración del proyecto ERP Nexus actual.
    """

    def __init__(self, project_dir: Optional[Path] = None):
        self.project_dir = project_dir or Path.cwd()
        self.env_file = self.project_dir / ".env"

    @property
    def is_erp_project(self) -> bool:
        return (self.project_dir / "manage.py").exists()

    @property
    def modules_dir(self) -> Path:
        return self.project_dir / "modules"

    @property
    def settings_module(self) -> str:
        env = os.environ.get("DJANGO_SETTINGS_MODULE", "")
        if env:
            return env
        return "erp_nexus.settings.development"

    def get_env(self, key: str, default: str = "") -> str:
        """Lee variable del .env o del entorno."""
        value = os.environ.get(key)
        if value:
            return value

        if self.env_file.exists():
            for line in self.env_file.read_text().split("\n"):
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == key:
                    return v.strip().strip('"').strip("'")

        return default
