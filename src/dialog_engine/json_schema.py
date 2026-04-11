"""JSON Schema для корня файла диалога — для автодополнения и ``cli schema``."""

from __future__ import annotations

import copy
from typing import Any

# Упрощённая схема: условия описаны как произвольные объекты (расширяемость).
DIALOG_FILE_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/ShyDamn/dialog-engine/dialog.schema.json",
    "title": "DialogEngine dialog file",
    "oneOf": [
        {"type": "array", "items": {"$ref": "#/$defs/step"}},
        {
            "type": "object",
            "required": ["steps"],
            "properties": {
                "steps": {"type": "array", "items": {"$ref": "#/$defs/step"}},
            },
            "additionalProperties": True,
        },
    ],
    "$defs": {
        "step": {
            "type": "object",
            "required": ["id", "type", "text"],
            "properties": {
                "id": {"type": "string"},
                "type": {"type": "string"},
                "text": {"type": "string"},
                "required": {"type": "boolean"},
                "choices": {"type": "object", "additionalProperties": {"type": "string"}},
                "min": {"type": "integer"},
                "max": {"type": "integer"},
                "skip_when": {"$ref": "#/$defs/whenRule"},
                "show_when": {"$ref": "#/$defs/whenRule"},
            },
            "additionalProperties": True,
        },
        "whenRule": {
            "oneOf": [
                {"type": "object", "additionalProperties": True},
                {"type": "array", "items": {"type": "object", "additionalProperties": True}},
            ]
        },
    },
}


def get_dialog_json_schema() -> dict[str, Any]:
    """Возвращает копию схемы (можно сохранить как ``.schema.json``)."""
    return copy.deepcopy(DIALOG_FILE_SCHEMA)
