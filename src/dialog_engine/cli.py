"""CLI: проверка JSON-файлов диалога."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dialog-engine-validate",
        description="Validate dialog JSON (syntax + optional Pydantic schema).",
    )
    parser.add_argument("path", type=Path, help="Path to .json dialog file")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Require pydantic validation (needs: pip install dialog-engine[validation])",
    )
    args = parser.parse_args(argv)

    path: Path = args.path
    if not path.is_file():
        print(f"Not a file: {path}", file=sys.stderr)
        return 2

    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as e:
        print(str(e), file=sys.stderr)
        return 1

    # Always try to build engine (core API)
    try:
        from dialog_engine.engine import DialogEngine

        if isinstance(data, dict):
            if "steps" not in data:
                print('JSON object must contain "steps" array', file=sys.stderr)
                return 1
            steps_payload = data["steps"]
        elif isinstance(data, list):
            steps_payload = data
        else:
            print("Root must be a JSON object or array", file=sys.stderr)
            return 1
        if not isinstance(steps_payload, list):
            print('"steps" must be a JSON array', file=sys.stderr)
            return 1
        DialogEngine.from_list(steps_payload)
    except Exception as e:
        print(f"DialogEngine load error: {e}", file=sys.stderr)
        return 1

    if args.strict:
        try:
            from dialog_engine.pydantic_schema import validate_dialog_data
        except ImportError:
            print(
                "Pydantic validation requested but pydantic is not installed. "
                "Use: pip install dialog-engine[validation]",
                file=sys.stderr,
            )
            return 3
        try:
            validate_dialog_data(data)
        except Exception as e:
            print(f"Pydantic validation error: {e}", file=sys.stderr)
            return 1

    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
