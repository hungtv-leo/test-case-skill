"""Chuan hoa ket qua test + phan loai coverage (verified vs gap)."""

from __future__ import annotations

_PASS_ALIASES = {"passed", "pass", "ok", "success", "true", "expected"}
_FAIL_ALIASES = {"failed", "fail", "false", "timedout", "unexpected", "flaky"}
_ERROR_ALIASES = {"error", "errored", "broken", "interrupted"}
_SKIP_ALIASES = {"skipped", "skip", "pending", "disabled", "todo"}

COVERAGE_VERIFIED = "verified"
COVERAGE_GAP_SET = {"gap", "exploratory", "needs-product-decision"}

# Nhan tieng Viet co dau — chi dung khi hien thi (Excel/bao cao). Enum JSON van la English.
COVERAGE_LABELS = {
    "verified": "Đã kiểm tra",
    "gap": "Lỗ hổng",
    "exploratory": "Khám phá",
    "needs-product-decision": "Chờ quyết định",
}

CATEGORY_LABELS = {
    "happy": "Thành công",
    "validate": "Kiểm tra dữ liệu",
    "auth": "Phân quyền",
    "state": "Trạng thái",
    "race": "Trùng request",
    "boundary": "Biên",
    "side-effect": "Tác dụng phụ",
    "dependency": "Phụ thuộc ngoài",
    "other": "Khác",
}


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


def coverage_label(value: str | None) -> str:
    raw = (value or "").strip().lower()
    return COVERAGE_LABELS.get(raw, value or "")


def category_label(value: str | None) -> str:
    raw = (value or "").strip().lower()
    return CATEGORY_LABELS.get(raw, value or "")


def get_coverage(meta) -> str:
    if not isinstance(meta, dict):
        return COVERAGE_VERIFIED
    raw = meta.get("coverage")
    if raw is None or str(raw).strip() == "":
        return COVERAGE_VERIFIED
    return str(raw).strip().lower()


def is_gap_case(meta) -> bool:
    return get_coverage(meta) in COVERAGE_GAP_SET


def partition_cases(cases: dict) -> tuple[dict, dict]:
    """Tach cases thanh (verified, gaps)."""
    verified = {}
    gaps = {}
    for test_id, meta in cases.items():
        if is_gap_case(meta):
            gaps[test_id] = meta
        else:
            verified[test_id] = meta
    return verified, gaps


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


def outcomes_from_any(data: dict) -> dict:
    """Chuan hoa moi dinh dang input ve map test_id -> outcome.

    - pytest-json-report (dict co key 'tests' la list)
    - flat map { test_id: "passed" | {"outcome"/"status": ...} }
    """
    if isinstance(data, dict) and isinstance(data.get("tests"), list):
        return outcomes_from_pytest_json_report(data)
    if not isinstance(data, dict):
        raise ValueError("results khong hop le: can object {test_id: outcome}")
    return outcomes_from_flat_map(data)


def pass_summary(outcomes: dict, cases: dict):
    """Tra ve (all_passed, passed, total, problems, case_ids) cho toan bo cases."""
    total = len(cases)
    passed = 0
    problems = []
    case_ids = []
    for test_id, meta in cases.items():
        cid = meta.get("case_id", test_id) if isinstance(meta, dict) else test_id
        case_ids.append(cid)
        outcome = outcomes.get(test_id)
        if outcome == "passed":
            passed += 1
        else:
            problems.append((cid, test_id, outcome or "no-result"))
    return passed == total and total > 0, passed, total, problems, case_ids


def verified_gate_summary(outcomes: dict, cases: dict):
    """Gate ban giao: CHI bat verified phai pass. Gap khong block.

    Tra ve:
      all_verified_passed, passed, total_verified, problems, verified_ids, gap_count
    """
    verified, gaps = partition_cases(cases)
    all_passed, passed, total, problems, case_ids = pass_summary(outcomes, verified)
    # Khong co verified nao: van cho ban giao neu chi co gap (exploratory handover)
    if total == 0:
        return True, 0, 0, [], [], len(gaps)
    return all_passed, passed, total, problems, case_ids, len(gaps)
