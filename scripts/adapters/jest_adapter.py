"""Adapter Jest / Vitest JSON output -> results.json chuan."""

from __future__ import annotations

from _lib.outcomes import normalize_outcome


def _walk_suites(suite: dict, prefix: str = "") -> dict:
    outcomes = {}
    file_path = suite.get("name") or prefix
    for assertion in suite.get("assertionResults", []):
        title = assertion.get("title") or assertion.get("fullName")
        if not title:
            continue
        status = assertion.get("status", "unknown")
        # Vitest/Jest: fullName thuong da day du; neu khong co thi ghep file + title
        test_id = assertion.get("fullName") or f"{file_path} > {title}"
        outcomes[test_id] = normalize_outcome(status)
    for child in suite.get("testResults", []):
        outcomes.update(_walk_suites(child, child.get("name", "")))
    return outcomes


def convert(data: dict) -> dict:
    if "testResults" in data and isinstance(data["testResults"], list):
        outcomes = {}
        for suite in data["testResults"]:
            outcomes.update(_walk_suites(suite))
        return outcomes
    if "assertionResults" in data:
        return _walk_suites(data)
    raise ValueError("Jest/Vitest JSON can co testResults hoac assertionResults")
