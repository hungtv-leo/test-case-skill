"""Validate cases.json va results.json theo JSON Schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator

from .outcomes import filter_test_entries, partition_cases

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
    return validate_outcomes_alignment(
        filter_test_entries(cases), filter_test_entries(results)
    )


def validate_outcomes_alignment(cases: dict, outcomes: dict) -> list[str]:
    """So khop id: verified BAT BUOC co trong results; gap duoc phep thieu.

    - Thieu verified trong results -> loi
    - Thua id trong results (khong co trong cases) -> loi
    - Gap khong co trong results -> OK (chua automate)
    """
    verified, _gaps = partition_cases(cases)
    problems = []
    missing_verified = sorted(set(verified.keys()) - set(outcomes.keys()))
    extra = sorted(set(outcomes.keys()) - set(cases.keys()))
    if missing_verified:
        problems.append("cases verified thieu ket qua trong results:")
        problems.extend(f"  - {test_id}" for test_id in missing_verified)
    if extra:
        problems.append("results co test id khong co trong cases.json:")
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
