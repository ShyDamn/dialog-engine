"""Экспорт схемы шагов в виде Mermaid flowchart (обзор порядка в конфиге)."""

from __future__ import annotations

from dialog_engine.engine import DialogEngine


def engine_to_mermaid(engine: DialogEngine, *, direction: str = "LR") -> str:
    """Строит линейную цепочку шагов по индексу (видимость в рантайме не учитывается).

    ``direction`` — одно из значений Mermaid: TB, BT, LR, RL.
    """
    d = direction.upper()
    if d not in {"TB", "BT", "LR", "RL"}:
        d = "LR"
    lines = [f"flowchart {d}"]
    steps = engine.steps
    for i, step in enumerate(steps):
        node_id = f"S{i}"
        label = step.id.replace('"', "'")
        lines.append(f'  {node_id}["{label}"]')
    for i in range(len(steps) - 1):
        lines.append(f"  S{i} --> S{i + 1}")
    return "\n".join(lines) + "\n"
