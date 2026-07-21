"""Chuyen doi output test framework -> results.json chuan.

Usage:
    python convert_results.py --framework pytest --input .report.json --output results.json
    python convert_results.py --framework vitest --input vitest-results.json --output results.json
    python convert_results.py --framework playwright --input playwright-report.json --output results.json
    python convert_results.py --framework go --input go-test.jsonl --output results.json
    python convert_results.py --framework junit --input target/surefire-reports/TEST-*.xml --output results.json
    python convert_results.py --framework remix --input report.json --output results.json --mode auto

Exit codes: 0 OK | 3 loi input/convert
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _lib.validate import load_json, validate_results  # noqa: E402
from adapters import FRAMEWORKS  # noqa: E402
from adapters import go_adapter, junit_adapter, remix_adapter  # noqa: E402

_JUNIT_KEYS = {"junit", "spring", "spring-boot"}
_GO_KEYS = {"go", "gotest"}


def _convert(framework: str, input_arg: str, mode: str | None = None) -> dict:
    key = framework.lower()
    if key not in FRAMEWORKS:
        supported = ", ".join(sorted(FRAMEWORKS))
        raise ValueError(f"Framework khong ho tro: {framework}. Ho tro: {supported}")
    # Cac framework doc thang tu file/glob (khong qua load_json)
    if key in _JUNIT_KEYS:
        return junit_adapter.convert_file(input_arg)
    if key in _GO_KEYS:
        return go_adapter.convert_file(input_arg)
    # Con lai: doc JSON roi convert
    data = load_json(input_arg)
    if key == "remix":
        return remix_adapter.convert(data, mode=mode or "auto")
    return FRAMEWORKS[key](data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert ket qua test framework -> results.json chuan.")
    parser.add_argument("--framework", required=True, help="pytest|vitest|jest|playwright|go|junit|spring-boot|remix|...")
    parser.add_argument("--input", required=True, help="File report dau vao")
    parser.add_argument("--output", required=True, help="File results.json dau ra")
    parser.add_argument(
        "--mode",
        choices=["auto", "unit", "e2e", "vitest", "playwright"],
        default="auto",
        help="Chi dung cho remix (unit=vitest, e2e=playwright)",
    )
    args = parser.parse_args()

    framework = args.framework.lower()
    is_glob = any(ch in args.input for ch in "*?[]")
    if not is_glob and not Path(args.input).exists():
        print(f"[ERROR] Khong tim thay file: {args.input}", file=sys.stderr)
        sys.exit(3)

    try:
        outcomes = _convert(framework, args.input, mode=args.mode)
    except (ValueError, FileNotFoundError, OSError, ET.ParseError, AttributeError, KeyError) as exc:
        print(f"[ERROR] Convert that bai: {exc}", file=sys.stderr)
        sys.exit(3)

    errors = validate_results(outcomes)
    if errors:
        print("[ERROR] Ket qua convert khong hop le schema:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(3)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(outcomes, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Da convert {len(outcomes)} test -> {args.output}")


if __name__ == "__main__":
    main()
