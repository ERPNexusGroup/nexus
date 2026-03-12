from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class RegistryEntry:
    name: str
    type: str  # file | url | github
    source: str
    is_default: bool = False


REGISTRY_FILE = Path.home() / ".nexus" / "registries.json"


def default_registry_entry() -> RegistryEntry:
    default_catalog = Path(__file__).resolve().parent / "catalogs" / "default.json"
    return RegistryEntry(
        name="default",
        type="file",
        source=str(default_catalog),
        is_default=True,
    )


def _load_raw() -> Dict:
    if not REGISTRY_FILE.exists():
        return {"registries": []}
    try:
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"registries": []}


def _save_raw(payload: Dict) -> None:
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def list_registries() -> List[RegistryEntry]:
    raw = _load_raw()
    result: List[RegistryEntry] = []
    for r in raw.get("registries", []):
        result.append(
            RegistryEntry(
                name=r.get("name", ""),
                type=r.get("type", "file"),
                source=r.get("source", ""),
                is_default=bool(r.get("default", False)),
            )
        )
    return result


def get_registry(name: Optional[str] = None) -> Optional[RegistryEntry]:
    regs = list_registries()
    if not regs:
        return default_registry_entry()
    if name:
        return next((r for r in regs if r.name == name), None)
    default = next((r for r in regs if r.is_default), None)
    return default or (regs[0] if regs else None)


def add_registry(entry: RegistryEntry) -> None:
    raw = _load_raw()
    registries = [r for r in raw.get("registries", []) if r.get("name") != entry.name]
    registries.append(
        {
            "name": entry.name,
            "type": entry.type,
            "source": entry.source,
            "default": entry.is_default,
        }
    )
    if entry.is_default:
        for r in registries:
            if r["name"] != entry.name:
                r["default"] = False
    raw["registries"] = registries
    _save_raw(raw)


def remove_registry(name: str) -> bool:
    raw = _load_raw()
    before = len(raw.get("registries", []))
    raw["registries"] = [r for r in raw.get("registries", []) if r.get("name") != name]
    _save_raw(raw)
    return len(raw["registries"]) != before


def set_default(name: str) -> bool:
    raw = _load_raw()
    found = False
    for r in raw.get("registries", []):
        if r.get("name") == name:
            r["default"] = True
            found = True
        else:
            r["default"] = False
    if found:
        _save_raw(raw)
    return found
