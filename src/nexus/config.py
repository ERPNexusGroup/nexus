from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NexusConfig:
    base_path: Path


def load_config() -> NexusConfig:
    """
    Carga configuración local desde ~/.nexus/config.json.
    """
    base_path = Path.home() / ".nexus" / "components"
    config_path = Path.home() / ".nexus" / "config.json"
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            base_path = Path(data.get("base_path", str(base_path)))
        except json.JSONDecodeError:
            pass
    return NexusConfig(base_path=base_path)
