"""Оценка видимости шага по контексту (skip_when / show_when)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from dialog_engine.step import DialogStep


def _get_field(context: Mapping[str, Any], field_name: str) -> Any:
    return context.get(field_name)


def _one_condition_matches(context: Mapping[str, Any], cond: dict[str, Any]) -> bool:
    """Одно условие: поддержка equals, in, not_in."""
    field_name = cond.get("field")
    if not field_name or not isinstance(field_name, str):
        return False
    value = _get_field(context, field_name)

    if "equals" in cond:
        return value == cond["equals"]
    if "in" in cond:
        allowed = cond["in"]
        if not isinstance(allowed, (list, tuple, set)):
            return False
        return value in allowed
    if "not_in" in cond:
        forbidden = cond["not_in"]
        if not isinstance(forbidden, (list, tuple, set)):
            return False
        return value not in forbidden
    return False


def _all_conditions_match(
    context: Mapping[str, Any],
    rules: dict[str, Any] | list[dict[str, Any]],
) -> bool:
    """Все условия (AND) выполняются."""
    if isinstance(rules, dict):
        return _one_condition_matches(context, rules)
    if isinstance(rules, list):
        if len(rules) == 0:
            return True
        return all(_one_condition_matches(context, c) for c in rules if isinstance(c, dict))
    return False


def step_is_visible(step: DialogStep, context: Mapping[str, Any]) -> bool:
    """Нужно ли показывать шаг при данном контексте."""
    if step.skip_when is not None and _all_conditions_match(context, step.skip_when):
        return False
    if step.show_when is not None:
        return _all_conditions_match(context, step.show_when)
    return True
