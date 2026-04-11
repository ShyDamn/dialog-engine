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


def test_skip_when_any_of() -> None:
    step = DialogStep.from_dict(
        {
            "id": "x",
            "type": "text",
            "text": "t",
            "skip_when": {
                "any_of": [
                    {"field": "role", "equals": "admin"},
                    {"field": "role", "equals": "mod"},
                ]
            },
        }
    )
    assert step_is_visible(step, {"role": "user"}) is True
    assert step_is_visible(step, {"role": "admin"}) is False
    assert step_is_visible(step, {"role": "mod"}) is False


def test_exists_and_numeric_compare() -> None:
    s1 = DialogStep.from_dict(
        {
            "id": "a",
            "type": "text",
            "text": "t",
            "show_when": {"field": "n", "exists": True},
        }
    )
    assert step_is_visible(s1, {}) is False
    assert step_is_visible(s1, {"n": None}) is False
    assert step_is_visible(s1, {"n": 0}) is True

    s2 = DialogStep.from_dict(
        {
            "id": "b",
            "type": "text",
            "text": "t",
            "skip_when": {"field": "age", "lt": 18},
        }
    )
    assert step_is_visible(s2, {"age": 20}) is True
    assert step_is_visible(s2, {"age": 10}) is False


def test_validate_engine_duplicate_ids() -> None:
    from dialog_engine.validation import validate_engine

    eng = DialogEngine.from_list(
        [
            {"id": "dup", "type": "text", "text": "a"},
            {"id": "dup", "type": "text", "text": "b"},
        ]
    )
    err = validate_engine(eng)
    assert any("duplicate" in e for e in err)


def test_dialog_session_state_roundtrip() -> None:
    from dialog_engine.state import DialogSessionState

    s = DialogSessionState(index=3, context={"k": "v"})
    s2 = DialogSessionState.from_json(s.to_json())
    assert s2.index == 3
    assert s2.context == {"k": "v"}


def test_mermaid_contains_ids() -> None:
    from dialog_engine.mermaid import engine_to_mermaid

    eng = DialogEngine.from_list(
        [
            {"id": "first", "type": "text", "text": "t"},
            {"id": "second", "type": "text", "text": "u"},
        ]
    )
    m = engine_to_mermaid(eng)
    assert "first" in m and "second" in m and "S0" in m


def test_aiogram_parse_choice() -> None:
    from dialog_engine.integrations.aiogram.keyboards import (
        KeyboardCallbacks,
        parse_choice_callback,
    )

    cb = KeyboardCallbacks()
    assert parse_choice_callback(cb.choice_data("step1", "yes"), cb) == ("step1", "yes")
    assert parse_choice_callback("other", cb) is None
