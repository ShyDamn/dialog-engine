"""Движок последовательности шагов и навигация с учётом видимости."""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

from dialog_engine.step import DialogStep
from dialog_engine.visibility import step_is_visible


class DialogEngine:
    """Управляет последовательностью шагов диалога."""

    def __init__(self, steps: list[DialogStep]) -> None:
        self.steps = steps

    @classmethod
    def from_file(cls, path: str | Path) -> DialogEngine:
        """Загружает диалог из JSON-файла.

        Поддерживает форматы ``{"steps": [...]}`` и голый список ``[...]``.
        """
        raw = Path(path).read_text(encoding="utf-8")
        return cls.from_json_string(raw)

    @classmethod
    def from_json_string(cls, raw: str) -> DialogEngine:
        data = json.loads(raw)
        steps_payload = data["steps"] if isinstance(data, dict) else data
        return cls.from_list(steps_payload)

    @classmethod
    def from_list(cls, data: list[dict[str, Any]]) -> DialogEngine:
        """Создаёт диалог из списка словарей."""
        return cls([DialogStep.from_dict(s) for s in data])

    def get_step(self, index: int) -> DialogStep | None:
        """Возвращает шаг по сырому индексу или None."""
        if 0 <= index < len(self.steps):
            return self.steps[index]
        return None

    def get_step_by_id(self, step_id: str) -> tuple[int, DialogStep] | None:
        """Ищет первый шаг с данным ``id``; возвращает (index, step) или None."""
        for idx, step in enumerate(self.steps):
            if step.id == step_id:
                return idx, step
        return None

    def total(self) -> int:
        """Общее число шагов в конфиге (без учёта скрытых)."""
        return len(self.steps)

    def is_last(self, index: int) -> bool:
        """Последний шаг по сырому индексу (как в оригинале)."""
        return index >= len(self.steps) - 1

    def visible_indices(self, context: Mapping[str, Any]) -> list[int]:
        """Индексы шагов, видимых при данном контексте, по порядку."""
        return [i for i, s in enumerate(self.steps) if step_is_visible(s, context)]

    def effective_total(self, context: Mapping[str, Any]) -> int:
        """Число видимых шагов."""
        return len(self.visible_indices(context))

    def effective_position(self, index: int, context: Mapping[str, Any]) -> int | None:
        """Позиция сырого индекса среди видимых (1-based) или None если шаг скрыт."""
        visible = self.visible_indices(context)
        try:
            pos = visible.index(index)
        except ValueError:
            return None
        return pos + 1

    def next_index(self, current_index: int, context: Mapping[str, Any]) -> int | None:
        """Следующий видимый индекс после ``current_index`` или None если конец."""
        n = len(self.steps)
        for j in range(current_index + 1, n):
            step = self.steps[j]
            if step_is_visible(step, context):
                return j
        return None

    def previous_index(self, current_index: int, context: Mapping[str, Any]) -> int | None:
        """Предыдущий видимый индекс перед ``current_index`` или None."""
        for j in range(current_index - 1, -1, -1):
            step = self.steps[j]
            if step_is_visible(step, context):
                return j
        return None

    def is_last_visible(self, index: int, context: Mapping[str, Any]) -> bool:
        """Является ли ``index`` последним видимым шагом."""
        nxt = self.next_index(index, context)
        return nxt is None and step_is_visible(self.steps[index], context)

    def first_visible_index(self, context: Mapping[str, Any]) -> int | None:
        """Первый видимый индекс или None."""
        for i, s in enumerate(self.steps):
            if step_is_visible(s, context):
                return i
        return None

    def iter_visible_steps(self, context: Mapping[str, Any]) -> Iterator[tuple[int, DialogStep]]:
        """Пары (index, step) только для видимых шагов."""
        for i, s in enumerate(self.steps):
            if step_is_visible(s, context):
                yield i, s

    def validation_errors(self) -> list[str]:
        """Проверка целостности (дубликаты ``id``, пустой список шагов и т.д.)."""
        from dialog_engine.validation import validate_engine

        return validate_engine(self)
