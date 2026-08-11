"""Tom tat gap / rui ro tu cases.json (va ket qua neu co).

Usage:
    python report_gaps.py --cases workdir/tests/<feature>/cases.json
    python report_gaps.py --cases ... --results workdir/results.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _lib.outcomes import (  # noqa: E402
    get_coverage,
    outcomes_from_any,
    partition_cases,
)
from _lib.validate import ensure_cases, load_json  # noqa: E402


def _safe_print(text: str = "") -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", errors="replace").decode("ascii"))


def _priority_key(meta: dict) -> str:
    return meta.get("priority") or "P?"


def main() -> None:
    parser = argparse.ArgumentParser(description="Bao cao gap/rui ro tu cases.json.")
    parser.add_argument("--cases", required=True, help="cases.json")
    parser.add_argument("--results", help="results.json (tuy chon)")
    parser.add_argument("--json-out", help="Ghi gaps.json (tuy chon)")
    args = parser.parse_args()

    try:
        raw_cases = load_json(args.cases)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(3)

    cases = ensure_cases(raw_cases, args.cases)
    outcomes = {}
    if args.results:
        try:
            outcomes = outcomes_from_any(load_json(args.results))
        except (FileNotFoundError, ValueError) as exc:
            print(f"[ERROR] {exc}", file=sys.stderr)
            sys.exit(3)

    verified, gaps = partition_cases(cases)
    _safe_print(f"Tong case: {len(cases)} | Verified: {len(verified)} | Gap/rui ro: {len(gaps)}")
    if not gaps:
        _safe_print("[OK] Khong co case gap/exploratory/needs-product-decision.")
        if args.json_out:
            Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
            Path(args.json_out).write_text("{}", encoding="utf-8")
        return

    by_priority: dict[str, list] = {}
    export = {}
    for test_id, meta in gaps.items():
        pri = _priority_key(meta)
        by_priority.setdefault(pri, []).append((test_id, meta))
        export[test_id] = {
            "case_id": meta.get("case_id", test_id),
            "coverage": get_coverage(meta),
            "category": meta.get("category"),
            "priority": meta.get("priority"),
            "description": meta.get("description"),
            "code_evidence": meta.get("code_evidence"),
            "risk": meta.get("risk"),
            "tester_note": meta.get("tester_note"),
            "outcome": outcomes.get(test_id),
        }

    for pri in sorted(by_priority.keys()):
        _safe_print(f"\n== {pri} ({len(by_priority[pri])}) ==")
        for test_id, meta in by_priority[pri]:
            cid = meta.get("case_id", test_id)
            cov = get_coverage(meta)
            cat = meta.get("category") or "-"
            outcome = outcomes.get(test_id)
            status = outcome if outcome else "chua-automate"
            _safe_print(f"- {cid} [{cov}/{cat}] {meta.get('description', '')}")
            _safe_print(f"  evidence: {meta.get('code_evidence', '')}")
            _safe_print(f"  risk: {meta.get('risk', '')}")
            _safe_print(f"  status: {status}")

    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(export, ensure_ascii=False, indent=2), encoding="utf-8")
        _safe_print(f"\n[OK] Da ghi {args.json_out}")


if __name__ == "__main__":
    main()
