from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NexusConfig:
    mode: str
    base_path: Path


def load_config(override_mode: str | None = None) -> NexusConfig:
    """
    Carga configuración local. Prioridad:
    1) override_mode
    2) env NEXUS_MODE
    3) config.json en ~/.nexus
    4) default (self_hosted)
    """
    base_path = Path.home() / ".nexus" / "components"
    config_path = Path.home() / ".nexus" / "config.json"
    mode = "self_hosted"

    env_mode = os.getenv("NEXUS_MODE")
    if env_mode:
        mode = env_mode

    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            mode = data.get("mode", mode)
            base_path = Path(data.get("base_path", str(base_path)))
        except json.JSONDecodeError:
            pass

    if override_mode:
        mode = override_mode

    return NexusConfig(mode=mode, base_path=base_path)
