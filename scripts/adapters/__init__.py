"""Adapter registry cho convert_results.py."""

from __future__ import annotations

from . import go_adapter, jest_adapter, junit_adapter, playwright_adapter, pytest_adapter, remix_adapter

FRAMEWORKS = {
    "pytest": pytest_adapter.convert,
    "jest": jest_adapter.convert,
    "vitest": jest_adapter.convert,
    "playwright": playwright_adapter.convert,
    "go": go_adapter.convert,
    "gotest": go_adapter.convert,
    "junit": junit_adapter.convert_file,
    "spring": junit_adapter.convert_file,
    "spring-boot": junit_adapter.convert_file,
    "remix": remix_adapter.convert,
    "remix-unit": lambda data: remix_adapter.convert(data, mode="unit"),
    "remix-e2e": lambda data: remix_adapter.convert(data, mode="e2e"),
}

GO_LINE_FORMATS = {"go", "gotest"}
