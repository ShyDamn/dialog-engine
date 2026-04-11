"""Модель шага диалога (JSON-конфиг)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DialogStep:
    """Один шаг пошагового диалога."""

    id: str
    type: str  # text | photo | choice
    text: str
    required: bool = True
    choices: dict[str, str] = field(default_factory=dict)
    min_photos: int = 1
    max_photos: int = 1
    # Декларативная видимость: если skip_when выполняется — шаг пропускается.
    # Если задан show_when — шаг показывается только когда условие выполняется.
    skip_when: dict[str, Any] | list[dict[str, Any]] | None = None
    show_when: dict[str, Any] | list[dict[str, Any]] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DialogStep:
        """Создаёт шаг из словаря JSON-конфига."""
        return cls(
            id=data["id"],
            type=data["type"],
            text=data["text"],
            required=data.get("required", True),
            choices=data.get("choices", {}),
            min_photos=data.get("min", 1),
            max_photos=data.get("max", 1),
            skip_when=data.get("skip_when"),
            show_when=data.get("show_when"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Сериализация в словарь (для отладки и тестов)."""
        d: dict[str, Any] = {
            "id": self.id,
            "type": self.type,
            "text": self.text,
            "required": self.required,
            "choices": dict(self.choices),
            "min": self.min_photos,
            "max": self.max_photos,
        }
        if self.skip_when is not None:
            d["skip_when"] = self.skip_when
        if self.show_when is not None:
            d["show_when"] = self.show_when
        return d
