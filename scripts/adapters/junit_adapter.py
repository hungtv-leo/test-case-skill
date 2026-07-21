"""Adapter JUnit XML (Spring Boot / Maven Surefire / Gradle) -> results.json chuan.

Ho tro 1 file, nhieu file, hoac glob (vd target/surefire-reports/TEST-*.xml).
"""

from __future__ import annotations

import glob as _glob
import xml.etree.ElementTree as ET
from pathlib import Path

from _lib.outcomes import normalize_outcome


def _class_name(testcase) -> str:
    classname = testcase.attrib.get("classname", "")
    name = testcase.attrib.get("name", "")
    if classname and name:
        return f"{classname}::{name}"
    return classname or name or "unknown"


def _outcome_for_testcase(testcase) -> str:
    if testcase.find("failure") is not None:
        return "failed"
    if testcase.find("error") is not None:
        return "error"
    if testcase.find("skipped") is not None:
        return "skipped"
    return "passed"


def convert_xml(root: ET.Element) -> dict:
    outcomes = {}
    for testsuite in root.findall(".//testsuite"):
        for testcase in testsuite.findall("testcase"):
            test_id = _class_name(testcase)
            outcomes[test_id] = normalize_outcome(_outcome_for_testcase(testcase))
    if not outcomes and root.tag == "testsuite":
        for testcase in root.findall("testcase"):
            test_id = _class_name(testcase)
            outcomes[test_id] = normalize_outcome(_outcome_for_testcase(testcase))
    return outcomes


def _expand_paths(pattern: str | Path) -> list[Path]:
    pattern_str = str(pattern)
    path = Path(pattern_str)
    if path.is_dir():
        return sorted(path.glob("*.xml"))
    if any(ch in pattern_str for ch in "*?[]"):
        return sorted(Path(p) for p in _glob.glob(pattern_str))
    return [path] if path.exists() else []


def convert_file(pattern: str | Path) -> dict:
    files = _expand_paths(pattern)
    if not files:
        raise ValueError(f"JUnit XML khong tim thay file khop: {pattern}")
    outcomes: dict = {}
    for file_path in files:
        root = ET.parse(file_path).getroot()
        outcomes.update(convert_xml(root))
    if not outcomes:
        raise ValueError("JUnit XML khong co testcase nao")
    return outcomes
