"""Пошаговые диалоги из JSON/YAML: движок, навигация, опционально aiogram."""

from dialog_engine.engine import DialogEngine
from dialog_engine.step import DialogStep
from dialog_engine.visibility import step_is_visible

__all__ = [
    "DialogEngine",
    "DialogStep",
    "step_is_visible",
]

__version__ = "0.1.0"
__author__ = "Danila Shubin, Saveliy Khvostov"
