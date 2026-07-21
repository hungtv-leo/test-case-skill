"""Adapter Playwright JSON report -> results.json chuan.

Test id = "<suite chain> > <test title>" (kem "[project]" neu chay nhieu project).
Suite chain gom ca title cua suite goc (thuong la duong dan file) + cac describe long nhau.
"""

from __future__ import annotations

from _lib.outcomes import normalize_outcome


def _collect_specs(suite: dict, ancestors: list[str]) -> dict:
    outcomes = {}
    title = suite.get("title")
    chain = ancestors + ([title] if title else [])

    for spec in suite.get("specs", []):
        spec_title = spec.get("title") or ""
        spec_chain = chain + ([spec_title] if spec_title else [])
        for test in spec.get("tests", []):
            project = test.get("projectName") or test.get("projectId") or ""
            base_id = " > ".join(part for part in spec_chain if part)
            test_id = f"{base_id} [{project}]" if project else base_id
            if not test_id:
                continue
            results = test.get("results") or []
            if not results:
                # Playwright: co the dung status cua test khi khong co results
                outcomes[test_id] = normalize_outcome(test.get("status", "skipped"))
                continue
            status = results[-1].get("status", "unknown")
            outcomes[test_id] = normalize_outcome(status)

    for child in suite.get("suites", []):
        outcomes.update(_collect_specs(child, chain))
    return outcomes


def convert(data: dict) -> dict:
    if "suites" in data:
        outcomes = {}
        for suite in data["suites"]:
            outcomes.update(_collect_specs(suite, []))
        if not outcomes:
            raise ValueError("Playwright JSON khong co test nao")
        return outcomes
    if "specs" in data:
        return _collect_specs(data, [])
    raise ValueError("Playwright JSON can co suites hoac specs")
