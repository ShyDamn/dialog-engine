"""Строгая валидация JSON-диалогов (требует зависимость ``pydantic`` / extra ``validation``)."""

from __future__ import annotations

from typing import Any

from pydantic import AliasChoices, BaseModel, Field

__all__ = ["DialogStepModel", "validate_dialog_data"]


class DialogStepModel(BaseModel):
    """Схема одного шага; поля совместимы с :class:`~dialog_engine.step.DialogStep`."""

    id: str
    type: str
    text: str
    required: bool = True
    choices: dict[str, str] = Field(default_factory=dict)
    min_photos: int = Field(1, validation_alias=AliasChoices("min", "min_photos"))
    max_photos: int = Field(1, validation_alias=AliasChoices("max", "max_photos"))
    skip_when: dict[str, Any] | list[dict[str, Any]] | None = None
    show_when: dict[str, Any] | list[dict[str, Any]] | None = None

    model_config = {"extra": "ignore"}


def validate_dialog_data(data: dict[str, Any] | list[Any]) -> None:
    """Проверяет корень диалога; бросает ``pydantic.ValidationError`` при ошибке."""
    steps: list[Any]
    if isinstance(data, dict) and "steps" in data:
        steps = data["steps"]
    elif isinstance(data, list):
        steps = data
    else:
        raise ValueError('Root must be {"steps": [...]} or a list of step objects')
    if not isinstance(steps, list):
        raise ValueError("steps must be a list")
    for i, raw in enumerate(steps):
        if not isinstance(raw, dict):
            raise ValueError(f"steps[{i}] must be an object")
        DialogStepModel.model_validate(raw)
