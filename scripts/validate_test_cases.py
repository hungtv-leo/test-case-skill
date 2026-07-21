"""Validate cases.json va/hoac results.json theo JSON Schema.

Usage:
    python validate_test_cases.py --cases tests/feature/cases.json
    python validate_test_cases.py --results results.json
    python validate_test_cases.py --cases tests/feature/cases.json --results results.json
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _lib.validate import (  # noqa: E402
    load_json,
    validate_cases,
    validate_cases_results_alignment,
    validate_results,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate cases.json / results.json.")
    parser.add_argument("--cases", help="Duong dan cases.json")
    parser.add_argument("--results", help="Duong dan results.json")
    args = parser.parse_args()

    if not args.cases and not args.results:
        parser.error("Can it nhat --cases hoac --results")

    exit_code = 0
    cases_data = None
    results_data = None

    if args.cases:
        try:
            cases_data = load_json(args.cases)
        except (FileNotFoundError, ValueError) as exc:
            print(f"[ERROR] {exc}", file=sys.stderr)
            sys.exit(3)
        errors = validate_cases(cases_data)
        if errors:
            print(f"[ERROR] {args.cases} khong hop le:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            exit_code = 3
        else:
            print(f"[OK] {args.cases} hop le schema.")

    if args.results:
        try:
            results_data = load_json(args.results)
        except (FileNotFoundError, ValueError) as exc:
            print(f"[ERROR] {exc}", file=sys.stderr)
            sys.exit(3)
        errors = validate_results(results_data)
        if errors:
            print(f"[ERROR] {args.results} khong hop le:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            exit_code = 3
        else:
            print(f"[OK] {args.results} hop le schema.")

    if cases_data is not None and results_data is not None and exit_code == 0:
        alignment = validate_cases_results_alignment(cases_data, results_data)
        if alignment:
            print("[ERROR] cases.json va results.json khong khop test id:", file=sys.stderr)
            for line in alignment:
                print(line, file=sys.stderr)
            sys.exit(3)
        print("[OK] cases.json va results.json khop test id.")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
