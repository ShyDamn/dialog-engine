"""CLI: проверка JSON, вывод схемы, Mermaid, шаблон диалога."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SUBCOMMANDS = frozenset({"validate", "init", "schema", "mermaid"})


def _cmd_validate(args: argparse.Namespace) -> int:
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
        engine = DialogEngine.from_list(steps_payload)
        verr = engine.validation_errors()
        if verr:
            for line in verr:
                print(line, file=sys.stderr)
            return 1
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


def _cmd_init(args: argparse.Namespace) -> int:
    out: Path = args.output
    template = {
        "steps": [
            {
                "id": "welcome",
                "type": "text",
                "text": "welcome-message-key",
                "required": True,
            },
            {
                "id": "plan",
                "type": "choice",
                "text": "plan-question-key",
                "required": True,
                "choices": {"free": "plan-free", "pro": "plan-pro"},
            },
        ]
    }
    try:
        text = json.dumps(template, ensure_ascii=False, indent=2) + "\n"
        out.write_text(text, encoding="utf-8")
    except OSError as e:
        print(str(e), file=sys.stderr)
        return 1
    print(f"Wrote {out}")
    return 0


def _cmd_schema(_args: argparse.Namespace) -> int:
    from dialog_engine.json_schema import get_dialog_json_schema

    schema = get_dialog_json_schema()
    print(json.dumps(schema, ensure_ascii=False, indent=2))
    return 0


def _cmd_mermaid(args: argparse.Namespace) -> int:
    path: Path = args.path
    if not path.is_file():
        print(f"Not a file: {path}", file=sys.stderr)
        return 2
    try:
        from dialog_engine.engine import DialogEngine
        from dialog_engine.mermaid import engine_to_mermaid

        engine = DialogEngine.from_file(path)
        print(engine_to_mermaid(engine, direction=args.direction), end="")
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] not in _SUBCOMMANDS:
        argv = ["validate", *argv]

    parser = argparse.ArgumentParser(
        prog="dialog-engine",
        description="Dialog JSON tools: validate, schema, mermaid, init template.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_val = sub.add_parser("validate", help="Validate dialog JSON (syntax + engine + graph checks)")
    p_val.add_argument("path", type=Path, help="Path to .json dialog file")
    p_val.add_argument(
        "--strict",
        action="store_true",
        help="Require pydantic validation (needs: pip install dialog-engine[validation])",
    )
    p_val.set_defaults(func=_cmd_validate)

    p_init = sub.add_parser("init", help="Write a minimal dialog JSON template")
    p_init.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("dialog.json"),
        help="Output file path (default: dialog.json)",
    )
    p_init.set_defaults(func=_cmd_init)

    p_schema = sub.add_parser("schema", help="Print JSON Schema for dialog files to stdout")
    p_schema.set_defaults(func=_cmd_schema)

    p_mer = sub.add_parser("mermaid", help="Print Mermaid flowchart for step order in file")
    p_mer.add_argument("path", type=Path, help="Path to .json dialog file")
    p_mer.add_argument(
        "--direction",
        default="LR",
        help="Mermaid direction: TB, BT, LR, RL (default: LR)",
    )
    p_mer.set_defaults(func=_cmd_mermaid)

    args = parser.parse_args(argv)
    return int(args.func(args))


def main_validate(argv: list[str] | None = None) -> int:
    """Точка входа ``dialog-engine-validate``: только проверка файла (как раньше)."""
    a = list(sys.argv[1:] if argv is None else argv)
    return main(["validate", *a])


if __name__ == "__main__":
    raise SystemExit(main())
