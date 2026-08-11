"""Test schema (metadata key), coverage, alignment soft, gate verified."""

from _lib.outcomes import (
    category_label,
    coverage_label,
    normalize_outcome,
    outcomes_from_any,
    partition_cases,
    pass_summary,
    verified_gate_summary,
)
from _lib.validate import (
    validate_cases,
    validate_outcomes_alignment,
    validate_results,
)


def _verified(case_id="TC-01", **extra):
    base = {
        "case_id": case_id,
        "description": "ok",
        "precondition": "none",
        "steps": ["do it"],
        "expected": "HTTP 200",
        "coverage": "verified",
        "category": "happy",
        "priority": "P0",
    }
    base.update(extra)
    return base


def _gap(case_id="TC-G1", **extra):
    base = {
        "case_id": case_id,
        "description": "gap case",
        "precondition": "none",
        "steps": ["try twice"],
        "expected": "reject second call",
        "coverage": "gap",
        "category": "race",
        "priority": "P0",
        "code_evidence": "Service.X: no idempotent lock",
        "risk": "duplicate side effect",
    }
    base.update(extra)
    return base


def test_metadata_key_allowed_in_cases():
    cases = {"__NOTE__": "ghi chu noi bo", "tests/a.py::test_ok": _verified()}
    assert validate_cases(cases) == []


def test_gap_requires_evidence_and_risk():
    bad = {
        "gap:TC-X": {
            "case_id": "TC-X",
            "description": "x",
            "precondition": "",
            "steps": ["a"],
            "expected": "y",
            "coverage": "gap",
        }
    }
    assert validate_cases(bad) != []


def test_gap_valid_with_evidence():
    cases = {"gap:TC-G1": _gap()}
    assert validate_cases(cases) == []


def test_metadata_key_allowed_in_results():
    results = {"__NOTE__": "ghi chu", "tests/a.py::test_ok": "passed"}
    assert validate_results(results) == []


def test_results_reject_invalid_outcome():
    assert validate_results({"t": "boom"}) != []


def test_vietnamese_display_labels():
    assert coverage_label("gap") == "Lỗ hổng"
    assert coverage_label("verified") == "Đã kiểm tra"
    assert coverage_label("exploratory") == "Khám phá"
    assert category_label("race") == "Trùng request"
    assert category_label("validate") == "Kiểm tra dữ liệu"


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


def test_alignment_verified_required_gap_optional():
    cases = {
        "a": _verified("TC-01"),
        "gap:TC-G1": _gap(),
    }
    # gap missing from results is OK; verified present OK
    assert validate_outcomes_alignment(cases, {"a": "passed"}) == []
    # missing verified is NOT OK
    problems = validate_outcomes_alignment(cases, {})
    assert any("a" in line for line in problems)
    # extra result id not OK
    problems2 = validate_outcomes_alignment(cases, {"a": "passed", "ghost": "passed"})
    assert any("ghost" in line for line in problems2)


def test_partition_and_verified_gate():
    cases = {
        "a": _verified("TC-01"),
        "b": _verified("TC-02"),
        "gap:TC-G1": _gap(),
    }
    verified, gaps = partition_cases(cases)
    assert set(verified) == {"a", "b"}
    assert set(gaps) == {"gap:TC-G1"}

    ok, passed, total, problems, ids, gap_count = verified_gate_summary(
        {"a": "passed", "b": "passed"}, cases
    )
    assert ok and passed == 2 and total == 2 and gap_count == 1 and not problems

    ok2, *_rest = verified_gate_summary({"a": "passed", "b": "failed"}, cases)
    assert not ok2


def test_pass_summary():
    cases = {"a": _verified("TC-01"), "b": _verified("TC-02")}
    all_passed, passed, total, problems, ids = pass_summary(
        {"a": "passed", "b": "passed"}, cases
    )
    assert all_passed and passed == 2 and total == 2 and not problems
    all_passed2, *_ = pass_summary({"a": "passed", "b": "failed"}, cases)
    assert not all_passed2


def test_templates_validate():
    from pathlib import Path
    import json

    root = Path(__file__).resolve().parents[2]
    cases = json.loads((root / "templates" / "cases.example.json").read_text(encoding="utf-8-sig"))
    results = json.loads((root / "templates" / "results.example.json").read_text(encoding="utf-8-sig"))
    assert validate_cases(cases) == []
    assert validate_results(results) == []
    from _lib.outcomes import filter_test_entries, outcomes_from_any

    assert validate_outcomes_alignment(filter_test_entries(cases), outcomes_from_any(results)) == []
