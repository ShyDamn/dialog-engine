"""Снимок состояния сессии диалога (индекс + контекст) для сохранения/восстановления."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass
class DialogSessionState:
    """Текущий сырой индекс шага и собранный контекст."""

    index: int
    context: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": 1,
            "index": self.index,
            "context": dict(self.context),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DialogSessionState:
        ver = data.get("version", 1)
        if ver != 1:
            raise ValueError(f"unsupported DialogSessionState version: {ver}")
        return cls(index=int(data["index"]), context=dict(data.get("context", {})))

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, raw: str) -> DialogSessionState:
        return cls.from_dict(json.loads(raw))
