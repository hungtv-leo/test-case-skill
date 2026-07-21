"""Adapter registry cho convert_results.py.

- FRAMEWORKS: map framework key -> callable(data-dict) -> outcomes.
  (Dung cho input da la JSON dict.)
- FILE_FORMATS: cac framework doc thang tu file/glob (go, junit) -> convert_file(path).
"""

from __future__ import annotations

from . import go_adapter, jest_adapter, junit_adapter, playwright_adapter, pytest_adapter, remix_adapter

FRAMEWORKS = {
    "pytest": pytest_adapter.convert,
    "jest": jest_adapter.convert,
    "vitest": jest_adapter.convert,
    "playwright": playwright_adapter.convert,
    "go": go_adapter.convert_file,
    "gotest": go_adapter.convert_file,
    "junit": junit_adapter.convert_file,
    "spring": junit_adapter.convert_file,
    "spring-boot": junit_adapter.convert_file,
    "remix": remix_adapter.convert,
    "remix-unit": lambda data: remix_adapter.convert(data, mode="unit"),
    "remix-e2e": lambda data: remix_adapter.convert(data, mode="e2e"),
}

# Framework doc tu file/glob thay vi JSON dict
FILE_FORMATS = {"go", "gotest", "junit", "spring", "spring-boot"}

# Backward-compat alias
GO_LINE_FORMATS = {"go", "gotest"}
