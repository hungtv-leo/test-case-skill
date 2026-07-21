"""Adapter Playwright JSON report -> results.json chuan."""

from __future__ import annotations

from _lib.outcomes import normalize_outcome


def _collect_specs(suite: dict, prefix: str = "") -> dict:
    outcomes = {}
    title = suite.get("title") or prefix
    for spec in suite.get("specs", []):
        spec_title = spec.get("title") or title
        for test in spec.get("tests", []):
            test_title = test.get("title") or spec_title
            test_id = f"{title} > {spec_title} > {test_title}".strip(" >")
            results = test.get("results") or []
            if not results:
                outcomes[test_id] = "skipped"
                continue
            status = results[-1].get("status", "unknown")
            outcomes[test_id] = normalize_outcome(status)
    for child in suite.get("suites", []):
        child_title = child.get("title") or title
        outcomes.update(_collect_specs(child, child_title))
    return outcomes


def convert(data: dict) -> dict:
    if "suites" in data:
        outcomes = {}
        for suite in data["suites"]:
            outcomes.update(_collect_specs(suite))
        return outcomes
    if "specs" in data:
        return _collect_specs(data)
    raise ValueError("Playwright JSON can co suites hoac specs")
