"""Оценка видимости шага по контексту (skip_when / show_when)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from dialog_engine.step import DialogStep


def _get_field(context: Mapping[str, Any], field_name: str) -> Any:
    return context.get(field_name)


def _compare_ordered(a: Any, b: Any) -> tuple[int | None, bool]:
    """Возвращает (cmp_result, ok) где cmp_result как для cmp: -1,0,1 или None если несравнимо."""
    try:
        if a == b:
            return 0, True
        if a < b:  # type: ignore[operator]
            return -1, True
        if a > b:  # type: ignore[operator]
            return 1, True
    except (TypeError, ValueError):
        return None, False
    return None, False


def _leaf_condition_matches(context: Mapping[str, Any], cond: dict[str, Any]) -> bool:
    """Одно листовое условие (без any_of / all_of)."""
    field_name = cond.get("field")
    if not field_name or not isinstance(field_name, str):
        return False
    value = _get_field(context, field_name)
    key_present = field_name in context

    if "exists" in cond:
        want = cond["exists"]
        if not isinstance(want, bool):
            return False
        if want:
            return key_present and value is not None
        return not key_present or value is None

    if not key_present:
        value = None

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
    for op, key in (("lt", "lt"), ("gt", "gt"), ("lte", "lte"), ("gte", "gte")):
        if key in cond:
            other = cond[key]
            cmp, ok = _compare_ordered(value, other)
            if not ok or cmp is None:
                return False
            if op == "lt":
                return cmp == -1
            if op == "gt":
                return cmp == 1
            if op == "lte":
                return cmp in (-1, 0)
            if op == "gte":
                return cmp in (0, 1)
    return False


def _rule_matches(context: Mapping[str, Any], cond: dict[str, Any]) -> bool:
    """Одно правило: лист, any_of (ИЛИ), all_of (И)."""
    if "any_of" in cond:
        subs = cond["any_of"]
        if not isinstance(subs, list):
            return False
        return any(_rule_matches(context, c) for c in subs if isinstance(c, dict))
    if "all_of" in cond:
        subs = cond["all_of"]
        if not isinstance(subs, list):
            return False
        if len(subs) == 0:
            return True
        return all(_rule_matches(context, c) for c in subs if isinstance(c, dict))
    return _leaf_condition_matches(context, cond)


def _all_conditions_match(
    context: Mapping[str, Any],
    rules: dict[str, Any] | list[dict[str, Any]],
) -> bool:
    """Все перечисленные правила (AND) выполняются."""
    if isinstance(rules, dict):
        return _rule_matches(context, rules)
    if isinstance(rules, list):
        if len(rules) == 0:
            return True
        return all(_rule_matches(context, c) for c in rules if isinstance(c, dict))
    return False


def step_is_visible(step: DialogStep, context: Mapping[str, Any]) -> bool:
    """Нужно ли показывать шаг при данном контексте."""
    if step.skip_when is not None and _all_conditions_match(context, step.skip_when):
        return False
    if step.show_when is not None:
        return _all_conditions_match(context, step.show_when)
    return True
