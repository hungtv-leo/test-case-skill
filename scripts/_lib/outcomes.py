"""Chuan hoa ket qua test ve map test_id -> outcome."""

from __future__ import annotations

_PASS_ALIASES = {"passed", "pass", "ok", "success", "true"}
_FAIL_ALIASES = {"failed", "fail", "false"}
_ERROR_ALIASES = {"error", "errored", "broken"}
_SKIP_ALIASES = {"skipped", "skip", "pending", "disabled"}


def normalize_outcome(value) -> str:
    text = str(value).strip().lower()
    if text in _PASS_ALIASES:
        return "passed"
    if text in _FAIL_ALIASES:
        return "failed"
    if text in _ERROR_ALIASES:
        return "error"
    if text in _SKIP_ALIASES:
        return "skipped"
    return text


def is_metadata_key(key: str) -> bool:
    return key.startswith("__") and key.endswith("__")


def filter_test_entries(data: dict) -> dict:
    return {k: v for k, v in data.items() if not is_metadata_key(k)}


def outcomes_from_flat_map(data: dict) -> dict:
    outcomes = {}
    for key, val in filter_test_entries(data).items():
        if isinstance(val, str):
            outcomes[key] = normalize_outcome(val)
        elif isinstance(val, dict):
            raw = val.get("outcome", val.get("status", "unknown"))
            outcomes[key] = normalize_outcome(raw)
        else:
            outcomes[key] = normalize_outcome(val)
    return outcomes


def outcomes_from_pytest_json_report(data: dict) -> dict:
    tests = data.get("tests")
    if not isinstance(tests, list):
        raise ValueError("pytest-json-report can co key 'tests' la list")
    outcomes = {}
    for test in tests:
        nodeid = test.get("nodeid")
        if nodeid:
            outcomes[nodeid] = normalize_outcome(test.get("outcome", "unknown"))
    return outcomes
