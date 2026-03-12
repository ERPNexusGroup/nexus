from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import tempfile
import urllib.request
import urllib.error
from urllib.parse import urlparse, unquote
import zipfile
import tarfile


@dataclass(frozen=True)
class CatalogItem:
    technical_name: str
    version: str
    description: str | None = None
    source: str | None = None


class CatalogError(Exception):
    pass


def load_catalog_from_source(source: str) -> List[CatalogItem]:
    """
    Carga catálogo en formato Version B desde:
    - file:// o ruta local
    - url http(s)
    """
    if source.startswith("http://") or source.startswith("https://"):
        try:
            with urllib.request.urlopen(source) as resp:
                data = resp.read().decode("utf-8")
        except urllib.error.URLError as e:
            raise CatalogError(f"No se pudo descargar catálogo: {e}") from e
    else:
        path = Path(source.replace("file://", ""))
        if not path.exists():
            raise CatalogError(f"No se encontró catálogo local en {path}.")
        data = path.read_text(encoding="utf-8")

    try:
        payload = json.loads(data)
    except json.JSONDecodeError as e:
        raise CatalogError(f"Catálogo JSON inválido: {e}") from e

    items: list[CatalogItem] = []
    for item in payload.get("items", []):
        versions = item.get("versions", [])
        for v in versions:
            items.append(
                CatalogItem(
                    technical_name=item.get("technical_name", ""),
                    version=v.get("version", ""),
                    description=item.get("description"),
                    source=v.get("source"),
                )
            )
    return items


def download_and_extract(source: str, technical_name: str, dest_dir: Path | None = None) -> Path:
    """
    Descarga un paquete y lo extrae en un directorio temporal o destino.
    Soporta http(s) y file:// (para pruebas).
    """
    target_dir = dest_dir or Path(tempfile.mkdtemp(prefix="nexus_pkg_"))
    target_dir.mkdir(parents=True, exist_ok=True)

    if source.startswith("file://"):
        parsed = urlparse(source)
        path = unquote(parsed.path)
        # Windows file URLs: /C:/path -> C:/path
        if len(path) >= 3 and path[0] == "/" and path[2] == ":":
            path = path[1:]
        if parsed.netloc:
            path = f"{parsed.netloc}{path}"
        archive_path = Path(path)
    elif source.startswith("http://") or source.startswith("https://"):
        archive_path = target_dir / f"{technical_name}.pkg"
        try:
            urllib.request.urlretrieve(source, archive_path)
        except urllib.error.URLError as e:
            raise CatalogError(f"No se pudo descargar paquete: {e}") from e
    else:
        archive_path = Path(source)
        if not archive_path.exists():
            raise CatalogError(f"No se encontró paquete local en {archive_path}.")

    extracted_root = target_dir / technical_name
    extracted_root.mkdir(parents=True, exist_ok=True)

    if zipfile.is_zipfile(archive_path):
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(extracted_root)
    elif tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path, "r:*") as tf:
            tf.extractall(extracted_root)
    else:
        raise CatalogError("Formato de paquete no soportado (use zip/tar.gz).")

    # Detectar carpeta raíz real
    candidates = [p for p in extracted_root.iterdir() if p.is_dir()]
    if len(candidates) == 1 and (candidates[0] / "__meta__.py").exists():
        return candidates[0]
    if (extracted_root / "__meta__.py").exists():
        return extracted_root

    raise CatalogError("No se encontró __meta__.py en el paquete extraído.")


def update_catalog_stub(destination: Optional[Path] = None) -> Path:
    """
    Stub de actualización de catálogo remoto.
    Crea/actualiza un JSON local con items de ejemplo.
    """
    catalog_path = destination or (Path.home() / ".nexus" / "catalog.json")
    catalog_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "items": [
            {
                "technical_name": "core_auth",
                "description": "Auth core",
                "versions": [
                    {
                        "version": "0.1.0",
                        "source": "https://example.com/core_auth-0.1.0.zip"
                    }
                ],
            },
            {
                "technical_name": "core_users",
                "description": "Users core",
                "versions": [
                    {
                        "version": "0.1.0",
                        "source": "https://example.com/core_users-0.1.0.zip"
                    }
                ],
            },
        ]
    }
    catalog_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return catalog_path
