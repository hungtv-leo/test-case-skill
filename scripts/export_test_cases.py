"""Xuat file Excel ban giao test-case cho tester (portable, da ngon ngu).

Join ket qua test voi metadata `cases.json` (khoa theo test id), CHI xuat khi
TAT CA case pass.

Dau vao ket qua (--results) chap nhan 2 dinh dang:
  1. results.json CHUAN (khuyen dung, moi ngon ngu):
        { "<test id>": "passed" | "failed" | "error" | "skipped", ... }
     (ho tro ca dang { "<test id>": {"outcome"/"status": "passed"} })
  2. pytest-json-report (.report.json): co key "tests" la list -> tu parse.

Usage:
    python export_test_cases.py \
        --results results.json \
        --cases <path>/cases.json \
        --out .selftest_tmp/handover_<feature>.xlsx

Exit codes:
    0  -> xuat thanh cong (tat ca pass)
    2  -> co case fail/error/khong chay -> KHONG xuat, in danh sach loi
    3  -> loi input (thieu file, sai dinh dang, test id khong khop)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _lib.outcomes import outcomes_from_any  # noqa: E402
from _lib.validate import (  # noqa: E402
    ensure_cases,
    load_json,
    validate_outcomes_alignment,
)

COLUMNS = [
    ("case_id", "Mã case", 14),
    ("description", "Mô tả", 40),
    ("precondition", "Điều kiện tiên đề", 30),
    ("steps", "Các bước", 45),
    ("data", "Dữ liệu", 30),
    ("expected", "Kết quả mong đợi", 35),
    ("actual", "Kết quả thực tế", 35),
    ("status", "Trạng thái", 12),
]


def _normalize_cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return "\n".join(f"{i + 1}. {step}" for i, step in enumerate(value))
    if isinstance(value, dict):
        return "\n".join(f"{k}: {v}" for k, v in value.items())
    return str(value)


def _write_excel(rows: list, out_path: str) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Test cases"

    header_fill = PatternFill("solid", fgColor="4472C4")
    header_font = Font(bold=True, color="FFFFFF")
    wrap = Alignment(vertical="top", wrap_text=True)

    for col_idx, (_, header, width) in enumerate(COLUMNS, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(vertical="center", horizontal="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    for row_idx, row in enumerate(rows, start=2):
        for col_idx, (key, _, _) in enumerate(COLUMNS, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=_normalize_cell(row.get(key)))
            cell.alignment = wrap

    ws.freeze_panes = "A2"
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Xuat Excel ban giao test-case (chi khi tat ca pass).")
    parser.add_argument("--results", required=True, help="results.json chuan hoac pytest .report.json")
    parser.add_argument("--cases", required=True, help="metadata cases.json (khoa theo test id)")
    parser.add_argument("--out", required=True, help="duong dan file .xlsx dau ra")
    args = parser.parse_args()

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

    rows = []
    problems = []

    for test_id, meta in cases.items():
        outcome = outcomes.get(test_id)
        row = dict(meta)
        row["case_id"] = meta.get("case_id", test_id)
        row["actual"] = meta.get("expected", "") if outcome == "passed" else f"[{outcome}]"
        row["status"] = "Pass" if outcome == "passed" else "Fail"
        rows.append(row)
        if outcome != "passed":
            problems.append((row["case_id"], test_id, outcome))

    if problems:
        print("[FAIL] Con case chua pass -> KHONG xuat Excel. Bao dev sua:", file=sys.stderr)
        for case_id, test_id, outcome in problems:
            print(f"  - {case_id} ({test_id}): {outcome}", file=sys.stderr)
        sys.exit(2)

    _write_excel(rows, args.out)
    print(f"[OK] Tat ca {len(rows)} case pass. Da xuat: {args.out}")


if __name__ == "__main__":
    main()
