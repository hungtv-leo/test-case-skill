"""Adapter Remix: unit/integration (Vitest) hoac E2E (Playwright)."""

from __future__ import annotations

from .jest_adapter import convert as convert_vitest
from .playwright_adapter import convert as convert_playwright


def convert(data: dict, mode: str = "auto") -> dict:
    if mode == "unit" or mode == "vitest":
        return convert_vitest(data)
    if mode == "e2e" or mode == "playwright":
        return convert_playwright(data)
    if "suites" in data or "specs" in data:
        return convert_playwright(data)
    if "testResults" in data or "assertionResults" in data:
        return convert_vitest(data)
    raise ValueError(
        "Khong nhan dien duoc dinh dang Remix. Dung --mode unit (Vitest) hoac --mode e2e (Playwright)."
    )
