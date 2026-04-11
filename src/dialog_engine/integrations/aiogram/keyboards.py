"""Inline-клавиатуры для шагов диалога (aiogram 3)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from dialog_engine.step import DialogStep

Translate = Callable[[str], str]


@dataclass(frozen=True)
class KeyboardCallbacks:
    """Значения ``callback_data``."""

    skip: str = "dialog_skip"
    back: str = "dialog_back"
    keep: str = "dialog_keep"
    photo_done: str = "dialog_photo_done"
    photo_clear: str = "dialog_photo_clear"
    choice_prefix: str = "dialog_choice"

    def choice_data(self, step_id: str, choice_key: str) -> str:
        return f"{self.choice_prefix}:{step_id}:{choice_key}"


def build_step_keyboard(
    step: DialogStep,
    translate: Translate,
    *,
    show_back: bool = True,
    current_value: str | None = None,
    keep_button_text: str | None = None,
    skip_label_key: str = "btn-skip",
    back_label_key: str = "btn-back",
    callbacks: KeyboardCallbacks | None = None,
) -> InlineKeyboardMarkup:
    """Клавиатура для шагов ``text`` и ``choice``.

    * ``translate(key)`` — подписи по i18n-ключам (как ``i18n.get(key)``).
    * Для кнопки «оставить» на текстовом шаге передайте готовую строку
      ``keep_button_text`` (например ``i18n.get("btn-keep", value=display)``).
    """
    cb = callbacks or KeyboardCallbacks()
    rows: list[list[InlineKeyboardButton]] = []

    if current_value and step.type == "text" and keep_button_text is not None:
        rows.append(
            [InlineKeyboardButton(text=keep_button_text, callback_data=cb.keep)]
        )

    if step.type == "choice":
        for key, label_key in step.choices.items():
            text = translate(label_key)
            if current_value == key:
                text = f"✅ {text}"
            rows.append(
                [
                    InlineKeyboardButton(
                        text=text,
                        callback_data=cb.choice_data(step.id, key),
                    )
                ]
            )

    if not step.required:
        rows.append(
            [InlineKeyboardButton(text=translate(skip_label_key), callback_data=cb.skip)]
        )
    if show_back:
        rows.append(
            [InlineKeyboardButton(text=translate(back_label_key), callback_data=cb.back)]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_photo_keyboard(
    translate: Translate,
    *,
    show_done: bool = False,
    show_keep: bool = False,
    keep_button_text: str | None = None,
    show_clear: bool = False,
    show_skip: bool = False,
    continue_label_key: str = "btn-continue",
    clear_label_key: str = "btn-clear-photos",
    skip_label_key: str = "btn-skip",
    back_label_key: str = "btn-back",
    callbacks: KeyboardCallbacks | None = None,
) -> InlineKeyboardMarkup:
    """Клавиатура для шага загрузки фото."""
    cb = callbacks or KeyboardCallbacks()
    rows: list[list[InlineKeyboardButton]] = []

    if show_keep and keep_button_text is not None:
        rows.append(
            [InlineKeyboardButton(text=keep_button_text, callback_data=cb.keep)]
        )
    if show_done:
        rows.append(
            [
                InlineKeyboardButton(
                    text=translate(continue_label_key), callback_data=cb.photo_done
                )
            ]
        )
    if show_clear:
        rows.append(
            [
                InlineKeyboardButton(
                    text=translate(clear_label_key), callback_data=cb.photo_clear
                )
            ]
        )
    if show_skip:
        rows.append(
            [InlineKeyboardButton(text=translate(skip_label_key), callback_data=cb.skip)]
        )
    rows.append(
        [InlineKeyboardButton(text=translate(back_label_key), callback_data=cb.back)]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)
