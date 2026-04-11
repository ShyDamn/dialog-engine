from __future__ import annotations

import json
from pathlib import Path

from dialog_engine import DialogEngine, DialogStep, step_is_visible
from dialog_engine.pydantic_schema import validate_dialog_data

DIALOGS = Path(__file__).resolve().parent.parent.parent / "dialogs"


def test_load_all_project_dialogs() -> None:
    for path in sorted(DIALOGS.glob("*.json")):
        engine = DialogEngine.from_file(path)
        assert engine.total() >= 1
        assert engine.get_step(0) is not None


def test_passport_eaeu_skip_bank_steps() -> None:
    path = DIALOGS / "passport_eaeu.json"
    engine = DialogEngine.from_file(path)
    ctx_self = {"card_owner": "self"}
    ctx_third = {"card_owner": "third"}
    assert engine.effective_total(ctx_self) == 12
    assert engine.effective_total(ctx_third) == 12
    bank = engine.get_step_by_id("bank_card_photo")
    assert bank is not None
    _bi, bstep = bank
    assert step_is_visible(bstep, ctx_third) is False
    assert step_is_visible(bstep, ctx_self) is True
    app = engine.get_step_by_id("bank_card_application_photo")
    assert app is not None
    _ai, ast = app
    assert step_is_visible(ast, ctx_self) is False
    assert step_is_visible(ast, ctx_third) is True


def test_next_previous_respects_visibility() -> None:
    path = DIALOGS / "passport_eaeu.json"
    engine = DialogEngine.from_file(path)
    ctx_self = {"card_owner": "self"}
    idx, _ = engine.get_step_by_id("bank_card_photo")
    assert engine.previous_index(idx, ctx_self) is not None
    # Последний шаг в JSON — application; для self он скрыт → после bank_card_photo конец
    assert engine.next_index(idx, ctx_self) is None
    ctx_third = {"card_owner": "third"}
    idx2, _ = engine.get_step_by_id("bank_card_application_photo")
    assert engine.next_index(idx2, ctx_third) is None


def test_pydantic_validate_dialog_file() -> None:
    raw = json.loads((DIALOGS / "rvp.json").read_text(encoding="utf-8"))
    validate_dialog_data(raw)


def test_dialog_step_from_dict_roundtrip() -> None:
    d = {
        "id": "x",
        "type": "text",
        "text": "k",
        "skip_when": {"field": "a", "equals": "b"},
    }
    s = DialogStep.from_dict(d)
    assert s.skip_when == {"field": "a", "equals": "b"}
