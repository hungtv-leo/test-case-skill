"""Comment ket qua self-test len Jira va dinh kem file Excel (portable).

CHI post khi TAT CA case pass (giong gate cua export). Ho tro Jira Server/DC
(PAT/Bearer) va Jira Cloud (email + API token qua Basic).

Ket qua test (--results) chap nhan 2 dinh dang giong export_test_cases.py:
    1. results.json CHUAN: { "<test id>": "passed" | "failed" | ... }
    2. pytest-json-report (.report.json): co key "tests".

Credentials lay tu env (KHONG hardcode). Tu dong nap tu file .env o goc repo
(tim bang cach leo cay thu muc tim .git hoac .env):
    JIRA_BASE_URL   vd: https://jira.congty.com  hoac https://xxx.atlassian.net
    JIRA_AUTH_MODE  'bearer' (PAT - Server/DC) hoac 'basic' (Cloud). Mac dinh 'bearer'.
    JIRA_TOKEN      PAT (bearer) hoac API token/password (basic)
    JIRA_USER       chi can cho basic (Cloud = email dang nhap)

Usage:
    # 1) Kiem tra ket noi + tu dong nhan dien loai Jira:
    python jira_notify.py --check

    # 2) Comment + dinh kem (chi khi tat ca pass):
    python jira_notify.py --issue TNV-123 \
        --results results.json \
        --cases <path>/cases.json \
        --xlsx .selftest_tmp/handover_<feature>.xlsx \
        --feature <feature>

Exit codes: 0 OK | 2 con case fail (khong post) | 3 loi input/env | 4 loi goi Jira
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import requests

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _lib.outcomes import outcomes_from_any, pass_summary  # noqa: E402
from _lib.validate import (  # noqa: E402
    ensure_cases,
    load_json,
    validate_outcomes_alignment,
)


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists() or (candidate / ".env").exists():
            return candidate
    return start


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    try:
        from dotenv import load_dotenv

        load_dotenv(path)
        return
    except Exception:
        pass
    try:
        for raw in path.read_text(encoding="utf-8-sig").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
    except Exception:
        pass


_load_env_file(_find_repo_root(Path.cwd()) / ".env")


def _env(name: str, default: str = None) -> str:
    return os.environ.get(name, default)


def _base_url() -> str:
    base = _env("JIRA_BASE_URL")
    if not base:
        print("[ERROR] Thieu env JIRA_BASE_URL", file=sys.stderr)
        sys.exit(3)
    return base.rstrip("/")


def _auth_kwargs() -> dict:
    mode = (_env("JIRA_AUTH_MODE", "bearer") or "bearer").lower()
    token = _env("JIRA_TOKEN")
    if not token:
        print("[ERROR] Thieu env JIRA_TOKEN", file=sys.stderr)
        sys.exit(3)
    if mode == "bearer":
        return {"headers": {"Authorization": f"Bearer {token}"}}
    if mode == "basic":
        user = _env("JIRA_USER")
        if not user:
            print("[ERROR] JIRA_AUTH_MODE=basic can them env JIRA_USER", file=sys.stderr)
            sys.exit(3)
        return {"auth": (user, token)}
    print(f"[ERROR] JIRA_AUTH_MODE khong hop le: {mode} (chi 'bearer' hoac 'basic')", file=sys.stderr)
    sys.exit(3)


def cmd_check() -> None:
    base = _base_url()
    auth = _auth_kwargs()
    url = f"{base}/rest/api/2/serverInfo"
    try:
        resp = requests.get(url, timeout=20, **auth)
    except requests.RequestException as exc:
        print(f"[ERROR] Khong ket noi duoc Jira: {exc}", file=sys.stderr)
        sys.exit(4)
    if resp.status_code == 401:
        print(
            "[ERROR] 401 - Sai credentials hoac auth mode. Neu la Jira Cloud, dung JIRA_AUTH_MODE=basic (email + API token).",
            file=sys.stderr,
        )
        sys.exit(4)
    if resp.status_code >= 400:
        print(f"[ERROR] serverInfo tra {resp.status_code}: {resp.text[:300]}", file=sys.stderr)
        sys.exit(4)
    info = resp.json()
    print("[OK] Ket noi Jira thanh cong.")
    print(f"  deploymentType: {info.get('deploymentType')}")
    print(f"  version:        {info.get('version')}")
    print(f"  baseUrl:        {info.get('baseUrl')}")


def _post_comment(base: str, auth: dict, issue: str, body: str) -> None:
    url = f"{base}/rest/api/2/issue/{issue}/comment"
    resp = requests.post(url, json={"body": body}, timeout=30, **auth)
    if resp.status_code == 404:
        print(f"[ERROR] Khong tim thay issue {issue} (404)", file=sys.stderr)
        sys.exit(4)
    if resp.status_code >= 400:
        print(f"[ERROR] Comment that bai {resp.status_code}: {resp.text[:300]}", file=sys.stderr)
        sys.exit(4)
    print(f"[OK] Da comment len {issue}")


def _upload_attachment(base: str, auth: dict, issue: str, xlsx: str) -> None:
    path = Path(xlsx)
    if not path.exists():
        print(f"[ERROR] Khong tim thay file dinh kem: {xlsx}", file=sys.stderr)
        sys.exit(3)
    url = f"{base}/rest/api/2/issue/{issue}/attachments"
    headers = dict(auth.get("headers", {}))
    headers["X-Atlassian-Token"] = "no-check"
    kwargs = {"headers": headers}
    if "auth" in auth:
        kwargs["auth"] = auth["auth"]
    with path.open("rb") as fh:
        files = {"file": (path.name, fh, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        resp = requests.post(url, files=files, timeout=60, **kwargs)
    if resp.status_code >= 400:
        print(f"[ERROR] Dinh kem that bai {resp.status_code}: {resp.text[:300]}", file=sys.stderr)
        sys.exit(4)
    print(f"[OK] Da dinh kem {path.name} vao {issue}")


def cmd_notify(args) -> None:
    try:
        raw_results = load_json(args.results)
        raw_cases = load_json(args.cases)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(3)

    cases = ensure_cases(raw_cases, args.cases)
    try:
        outcomes = outcomes_from_any(raw_results)
    except ValueError as exc:
        print(f"[ERROR] {args.results}: {exc}", file=sys.stderr)
        sys.exit(3)

    alignment = validate_outcomes_alignment(cases, outcomes)
    if alignment:
        print("[ERROR] cases.json va results khong khop test id:", file=sys.stderr)
        for line in alignment:
            print(line, file=sys.stderr)
        sys.exit(3)

    all_passed, passed, total, problems, case_ids = pass_summary(outcomes, cases)

    if not all_passed:
        print("[FAIL] Con case chua pass -> KHONG post len Jira:", file=sys.stderr)
        for cid, test_id, outcome in problems:
            print(f"  - {cid} ({test_id}): {outcome}", file=sys.stderr)
        sys.exit(2)

    feature = args.feature or "feature"
    xlsx_name = Path(args.xlsx).name if args.xlsx else "(khong co file)"
    ids_str = ", ".join(case_ids)
    body = (
        f"*[Self-test] {feature}*: {passed}/{total} case PASS.\n"
        f"File ban giao: {xlsx_name}" + (" (dinh kem)." if args.xlsx else ".") + "\n"
        f"Danh sach case: {ids_str}"
    )

    base = _base_url()
    auth = _auth_kwargs()
    _post_comment(base, auth, args.issue, body)
    if args.xlsx:
        _upload_attachment(base, auth, args.issue, args.xlsx)


def main() -> None:
    parser = argparse.ArgumentParser(description="Comment ket qua self-test len Jira.")
    parser.add_argument("--check", action="store_true", help="Kiem tra ket noi + nhan dien loai Jira")
    parser.add_argument("--issue", help="Issue key, vd TNV-123")
    parser.add_argument("--results", help="results.json chuan hoac pytest .report.json")
    parser.add_argument("--cases", help="cases.json")
    parser.add_argument("--xlsx", help="file Excel dinh kem (tuy chon)")
    parser.add_argument("--feature", help="ten tinh nang de hien trong comment")
    args = parser.parse_args()

    if args.check:
        cmd_check()
        return
    if not (args.issue and args.results and args.cases):
        parser.error("Can --issue, --results, --cases (hoac dung --check)")
    cmd_notify(args)


if __name__ == "__main__":
    main()
