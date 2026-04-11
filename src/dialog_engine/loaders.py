"""Дополнительные загрузчики (YAML — опционально, см. extra ``yaml``)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from dialog_engine.engine import DialogEngine


def from_yaml_file(path: str | Path) -> DialogEngine:
    """Загружает диалог из YAML-файла. Требует ``pip install dialog-engine[yaml]``."""
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as e:
        raise ImportError(
            "YAML support requires PyYAML. Install with: pip install dialog-engine[yaml]"
        ) from e
    raw = Path(path).read_text(encoding="utf-8")
    data: Any = yaml.safe_load(raw)
    steps_payload = data["steps"] if isinstance(data, dict) else data
    if not isinstance(steps_payload, list):
        raise ValueError("YAML root must be a list or {\"steps\": [...]}")
    return DialogEngine.from_list(steps_payload)
