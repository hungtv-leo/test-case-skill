"""Adapter go test -json (line-delimited JSON) -> results.json chuan."""

from __future__ import annotations

import json
from pathlib import Path

from _lib.outcomes import normalize_outcome


def _parse_event(event: dict, package: str, test_name: str) -> tuple[str, str] | None:
    action = event.get("Action") or event.get("action")
    if action != "pass" and action != "fail" and action != "skip":
        return None
    pkg = event.get("Package") or event.get("package") or package
    test = event.get("Test") or event.get("test") or test_name
    if not test:
        return None
    test_id = f"{pkg}::{test}" if pkg else test
    if action == "pass":
        return test_id, "passed"
    if action == "fail":
        return test_id, "failed"
    return test_id, "skipped"


def convert_from_lines(lines: list[str]) -> dict:
    outcomes = {}
    package = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("Action") == "run" or event.get("action") == "run":
            package = event.get("Package") or event.get("package") or package
        parsed = _parse_event(event, package, event.get("Test") or event.get("test") or "")
        if parsed:
            test_id, outcome = parsed
            outcomes[test_id] = normalize_outcome(outcome)
    return outcomes


def convert(data) -> dict:
    if isinstance(data, list):
        return convert_from_lines([json.dumps(item) for item in data])
    if isinstance(data, dict) and "events" in data:
        return convert_from_lines([json.dumps(item) for item in data["events"]])
    raise ValueError("Go test JSON can la list event hoac file line-delimited JSON")


def convert_file(path: str | Path) -> dict:
    text = Path(path).read_text(encoding="utf-8-sig")
    return convert_from_lines(text.splitlines())
