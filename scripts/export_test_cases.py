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
import argparse
import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

COLUMNS = [
    ("case_id", "Ma case", 14),
    ("description", "Mo ta", 40),
    ("precondition", "Dieu kien tien de", 30),
    ("steps", "Cac buoc", 45),
    ("data", "Du lieu", 30),
    ("expected", "Ket qua mong doi", 35),
    ("actual", "Ket qua thuc te", 35),
    ("status", "Trang thai", 12),
]

_PASS_ALIASES = {"passed", "pass", "ok", "success", "true"}


def _load_json(path: str) -> dict:
    file_path = Path(path)
    if not file_path.exists():
        print(f"[ERROR] Khong tim thay file: {path}", file=sys.stderr)
        sys.exit(3)
    try:
        return json.loads(file_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        print(f"[ERROR] File JSON khong hop le: {path} ({exc})", file=sys.stderr)
        sys.exit(3)


def _normalize_outcome(value) -> str:
    text = str(value).strip().lower()
    return "passed" if text in _PASS_ALIASES else text


def _outcomes_from_results(data: dict) -> dict:
    """Chuan hoa ket qua ve map test id -> outcome, ho tro nhieu dinh dang."""
    # pytest-json-report
    if isinstance(data, dict) and isinstance(data.get("tests"), list):
        outcomes = {}
        for test in data["tests"]:
            nodeid = test.get("nodeid")
            if nodeid:
                outcomes[nodeid] = _normalize_outcome(test.get("outcome", "unknown"))
        return outcomes
    # flat map: id -> "passed" hoac id -> {outcome/status}
    if not isinstance(data, dict):
        print("[ERROR] results khong hop le: can object {test_id: outcome}", file=sys.stderr)
        sys.exit(3)
    outcomes = {}
    for key, val in data.items():
        if isinstance(val, str):
            outcomes[key] = _normalize_outcome(val)
        elif isinstance(val, dict):
            raw = val.get("outcome", val.get("status", "unknown"))
            outcomes[key] = _normalize_outcome(raw)
        else:
            outcomes[key] = _normalize_outcome(val)
    return outcomes


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

    outcomes = _outcomes_from_results(_load_json(args.results))
    cases = _load_json(args.cases)

    rows = []
    problems = []
    missing_result = []

    for test_id, meta in cases.items():
        outcome = outcomes.get(test_id)
        if outcome is None:
            missing_result.append(test_id)
            continue
        row = dict(meta)
        row["case_id"] = meta.get("case_id", test_id)
        row["actual"] = meta.get("expected", "") if outcome == "passed" else f"[{outcome}]"
        row["status"] = "Pass" if outcome == "passed" else "Fail"
        rows.append(row)
        if outcome != "passed":
            problems.append((row["case_id"], test_id, outcome))

    if missing_result:
        print("[ERROR] Cac test id trong cases.json khong co ket qua trong results:", file=sys.stderr)
        for test_id in missing_result:
            print(f"  - {test_id}", file=sys.stderr)
        print("Kiem tra ten test id hoac chay lai test.", file=sys.stderr)
        sys.exit(3)

    if problems:
        print("[FAIL] Con case chua pass -> KHONG xuat Excel. Bao dev sua:", file=sys.stderr)
        for case_id, test_id, outcome in problems:
            print(f"  - {case_id} ({test_id}): {outcome}", file=sys.stderr)
        sys.exit(2)

    _write_excel(rows, args.out)
    print(f"[OK] Tat ca {len(rows)} case pass. Da xuat: {args.out}")


if __name__ == "__main__":
    main()
