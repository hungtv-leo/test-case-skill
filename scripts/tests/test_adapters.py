"""Unit test cho cac adapter convert -> results.json chuan."""

import json

from adapters import go_adapter, jest_adapter, junit_adapter, playwright_adapter, pytest_adapter, remix_adapter


def test_pytest_adapter_basic():
    data = {"tests": [
        {"nodeid": "tests/a.py::test_ok", "outcome": "passed"},
        {"nodeid": "tests/a.py::test_bad", "outcome": "failed"},
    ]}
    out = pytest_adapter.convert(data)
    assert out == {
        "tests/a.py::test_ok": "passed",
        "tests/a.py::test_bad": "failed",
    }


def test_jest_vitest_fullname_and_todo():
    data = {"testResults": [{
        "name": "src/a.test.ts",
        "assertionResults": [
            {"fullName": "a > works", "status": "passed", "title": "works"},
            {"fullName": "a > todo", "status": "todo", "title": "todo"},
        ],
    }]}
    out = jest_adapter.convert(data)
    assert out["a > works"] == "passed"
    assert out["a > todo"] == "skipped"


def test_playwright_nested_suites_and_project():
    data = {"suites": [{
        "title": "login.spec.ts",
        "suites": [{
            "title": "Login",
            "specs": [{
                "title": "invalid creds",
                "tests": [
                    {"projectName": "chromium", "results": [{"status": "passed"}]},
                    {"projectName": "firefox", "results": [{"status": "failed"}]},
                ],
            }],
        }],
    }]}
    out = playwright_adapter.convert(data)
    # Chain giu ca file + describe + spec, va tach theo project (khong ghi de)
    assert out["login.spec.ts > Login > invalid creds [chromium]"] == "passed"
    assert out["login.spec.ts > Login > invalid creds [firefox]"] == "failed"


def test_playwright_timedout_maps_to_failed():
    data = {"suites": [{
        "title": "a.spec.ts",
        "specs": [{"title": "slow", "tests": [{"results": [{"status": "timedOut"}]}]}],
    }]}
    out = playwright_adapter.convert(data)
    assert out["a.spec.ts > slow"] == "failed"


def test_go_adapter_jsonl():
    lines = [
        json.dumps({"Action": "run", "Package": "pkg/users", "Test": "TestOK"}),
        json.dumps({"Action": "pass", "Package": "pkg/users", "Test": "TestOK"}),
        json.dumps({"Action": "output", "Package": "pkg/users"}),
    ]
    out = go_adapter.convert_from_lines(lines)
    assert out == {"pkg/users::TestOK": "passed"}


def test_go_adapter_array_and_bad_lines():
    events = [
        {"Action": "fail", "Package": "p", "Test": "TestX"},
        "not-an-object",
    ]
    out = go_adapter.convert(events)
    assert out == {"p::TestX": "failed"}


def test_junit_multi_suite(tmp_path):
    xml = """<testsuites>
      <testsuite name="A"><testcase classname="com.A" name="ok"/></testsuite>
      <testsuite name="B"><testcase classname="com.B" name="bad"><failure/></testcase></testsuite>
    </testsuites>"""
    f = tmp_path / "TEST-a.xml"
    f.write_text(xml, encoding="utf-8")
    out = junit_adapter.convert_file(str(f))
    assert out["com.A::ok"] == "passed"
    assert out["com.B::bad"] == "failed"


def test_junit_glob(tmp_path):
    (tmp_path / "TEST-a.xml").write_text(
        '<testsuite name="A"><testcase classname="A" name="t1"/></testsuite>', encoding="utf-8"
    )
    (tmp_path / "TEST-b.xml").write_text(
        '<testsuite name="B"><testcase classname="B" name="t2"><skipped/></testcase></testsuite>',
        encoding="utf-8",
    )
    out = junit_adapter.convert_file(str(tmp_path / "TEST-*.xml"))
    assert out == {"A::t1": "passed", "B::t2": "skipped"}


def test_remix_mode_dispatch():
    vitest = {"testResults": [{"name": "a", "assertionResults": [
        {"fullName": "a > x", "status": "passed", "title": "x"}]}]}
    pw = {"suites": [{"title": "a.spec.ts", "specs": [
        {"title": "y", "tests": [{"results": [{"status": "passed"}]}]}]}]}
    assert remix_adapter.convert(vitest, mode="unit") == {"a > x": "passed"}
    assert remix_adapter.convert(pw, mode="e2e") == {"a.spec.ts > y": "passed"}
