"""Validate cases.json va results.json theo JSON Schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator

from .outcomes import filter_test_entries

_SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"


def _load_schema(name: str) -> dict:
    path = _SCHEMA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Khong tim thay schema: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_json(path: str | Path) -> dict:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Khong tim thay file: {path}")
    try:
        return json.loads(file_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"File JSON khong hop le: {path} ({exc})") from exc


def validate_cases(data: dict) -> list[str]:
    validator = Draft7Validator(_load_schema("cases.schema.json"))
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    return [f"{'.'.join(map(str, err.path)) or '<root>'}: {err.message}" for err in errors]


def validate_results(data: dict) -> list[str]:
    validator = Draft7Validator(_load_schema("results.schema.json"))
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    return [f"{'.'.join(map(str, err.path)) or '<root>'}: {err.message}" for err in errors]


def validate_cases_results_alignment(cases: dict, results: dict) -> list[str]:
    case_ids = set(filter_test_entries(cases).keys())
    result_ids = set(filter_test_entries(results).keys())
    problems = []
    missing = sorted(case_ids - result_ids)
    extra = sorted(result_ids - case_ids)
    if missing:
        problems.append("cases.json co test id khong co trong results.json:")
        problems.extend(f"  - {test_id}" for test_id in missing)
    if extra:
        problems.append("results.json co test id khong co trong cases.json:")
        problems.extend(f"  - {test_id}" for test_id in extra)
    return problems


def ensure_cases(data: dict, path: str = "cases.json") -> dict:
    errors = validate_cases(data)
    if errors:
        print(f"[ERROR] {path} khong hop le schema:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(3)
    test_cases = filter_test_entries(data)
    if not test_cases:
        print(f"[ERROR] {path} khong co test case nao (bo qua key __metadata__).", file=sys.stderr)
        sys.exit(3)
    return test_cases


def ensure_results(data: dict, path: str = "results.json") -> dict:
    errors = validate_results(data)
    if errors:
        print(f"[ERROR] {path} khong hop le schema:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(3)
    test_results = filter_test_entries(data)
    if not test_results:
        print(f"[ERROR] {path} khong co ket qua test nao.", file=sys.stderr)
        sys.exit(3)
    return test_results
