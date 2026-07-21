"""Adapter pytest-json-report -> results.json chuan."""

from __future__ import annotations

from _lib.outcomes import outcomes_from_pytest_json_report


def convert(data: dict) -> dict:
    return outcomes_from_pytest_json_report(data)
