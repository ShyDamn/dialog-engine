"""Проверка целостности загруженного диалога (граф шагов, уникальность id)."""

from __future__ import annotations

from collections import Counter

from dialog_engine.engine import DialogEngine


def validate_engine(engine: DialogEngine) -> list[str]:
    """Возвращает список сообщений об ошибках; пустой список — конфиг допустим."""
    errors: list[str] = []
    if not engine.steps:
        errors.append("dialog has no steps")
        return errors
    counts = Counter(s.id for s in engine.steps)
    dup = [i for i, n in counts.items() if n > 1]
    if dup:
        errors.append(f"duplicate step id(s): {', '.join(sorted(dup))}")
    return errors
