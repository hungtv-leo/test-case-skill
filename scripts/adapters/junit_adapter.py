"""Adapter JUnit XML (Spring Boot / Maven Surefire / Gradle) -> results.json chuan."""

from __future__ import annotations

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


def convert_file(path: str | Path) -> dict:
    root = ET.parse(path).getroot()
    outcomes = convert_xml(root)
    if not outcomes:
        raise ValueError("JUnit XML khong co testcase nao")
    return outcomes
