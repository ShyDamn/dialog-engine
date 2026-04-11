"""Пошаговые диалоги из JSON/YAML: движок, навигация, опционально aiogram."""

from dialog_engine.engine import DialogEngine
from dialog_engine.json_schema import DIALOG_FILE_SCHEMA, get_dialog_json_schema
from dialog_engine.mermaid import engine_to_mermaid
from dialog_engine.state import DialogSessionState
from dialog_engine.step import DialogStep
from dialog_engine.validation import validate_engine
from dialog_engine.visibility import step_is_visible

__all__ = [
    "DIALOG_FILE_SCHEMA",
    "DialogEngine",
    "DialogSessionState",
    "DialogStep",
    "engine_to_mermaid",
    "get_dialog_json_schema",
    "step_is_visible",
    "validate_engine",
]

__version__ = "0.1.1"
__author__ = "Danila Shubin, Saveliy Khvostov"
