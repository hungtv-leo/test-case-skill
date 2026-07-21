"""Test schema (metadata key) va cac helper outcomes/alignment."""

from _lib.outcomes import normalize_outcome, outcomes_from_any, pass_summary
from _lib.validate import (
    validate_cases,
    validate_outcomes_alignment,
    validate_results,
)


def test_metadata_key_allowed_in_cases():
    cases = {
        "__NOTE__": "ghi chu noi bo",
        "tests/a.py::test_ok": {
            "case_id": "TC-01",
            "description": "ok",
            "precondition": "none",
            "steps": ["do it"],
            "expected": "HTTP 200",
        },
    }
    assert validate_cases(cases) == []


def test_metadata_key_allowed_in_results():
    results = {"__NOTE__": "ghi chu", "tests/a.py::test_ok": "passed"}
    assert validate_results(results) == []


def test_results_reject_invalid_outcome():
    assert validate_results({"t": "boom"}) != []


def test_normalize_aliases():
    assert normalize_outcome("PASS") == "passed"
    assert normalize_outcome("timedOut") == "failed"
    assert normalize_outcome("interrupted") == "error"
    assert normalize_outcome("todo") == "skipped"


def test_outcomes_from_any_pytest_and_flat():
    pytest_report = {"tests": [{"nodeid": "a::t", "outcome": "passed"}]}
    assert outcomes_from_any(pytest_report) == {"a::t": "passed"}
    flat = {"a::t": "failed", "__NOTE__": "x"}
    assert outcomes_from_any(flat) == {"a::t": "failed"}


def test_alignment_reports_missing_and_extra():
    cases = {"a": {"case_id": "TC-01"}, "b": {"case_id": "TC-02"}}
    outcomes = {"a": "passed", "c": "passed"}
    problems = validate_outcomes_alignment(cases, outcomes)
    joined = "\n".join(problems)
    assert "b" in joined  # missing in results
    assert "c" in joined  # extra in results


def test_pass_summary():
    cases = {"a": {"case_id": "TC-01"}, "b": {"case_id": "TC-02"}}
    all_passed, passed, total, problems, ids = pass_summary({"a": "passed", "b": "passed"}, cases)
    assert all_passed and passed == 2 and total == 2 and not problems
    all_passed2, *_ = pass_summary({"a": "passed", "b": "failed"}, cases)
    assert not all_passed2
