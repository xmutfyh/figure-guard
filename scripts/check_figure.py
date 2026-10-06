#!/usr/bin/env python
"""The audit gate: run every check on one or more figure PDFs and exit non-zero if any is unclean.

WHY ONE COMMAND
---------------
The two audits are separate scripts with different outputs. Run by hand, it is easy to run one, see
it pass, and forget the other -- and the two catch different failures: the collision audit sees a
label crossed by a marker, the text audit sees a 4.34 pt exponent that no visual check would notice.
One command that runs both and reports a single verdict removes that choice.

Exit code 0 only when EVERY file is clean on BOTH audits.

Usage:
    python check_figure.py fig3a.pdf fig3b.pdf ...
    python check_figure.py --dir out/fig3
    python check_figure.py --json report.json out/fig3/*.pdf
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COLLISION = HERE / "audit_figure_collisions.py"
TEXT = HERE / "audit_pdf_text.py"


def run(script: Path, pdf: Path) -> str:
    r = subprocess.run([sys.executable, str(script), str(pdf)],
                       capture_output=True, text=True)
    return r.stdout + r.stderr


def parse_collision(out: str) -> dict:
    m = re.search(r"summary:\s*(\d+)\s*fail,\s*(\d+)\s*warn", out)
    fails = int(m.group(1)) if m else -1
    warns = int(m.group(2)) if m else -1
    findings = [ln.strip() for ln in out.splitlines() if "[FAIL]" in ln or "[WARN]" in ln]
    return {"fail": fails, "warn": warns, "findings": findings}


def parse_text(out: str) -> dict:
    mn = re.search(r"minimum found:\s*([\d.]+)\s*pt", out)
    bl = re.search(r"below minimum:\s*(\d+)", out)
    return {"minimum_pt": float(mn.group(1)) if mn else None,
            "below_minimum": int(bl.group(1)) if bl else -1}


def check(pdf: Path) -> dict:
    c = parse_collision(run(COLLISION, pdf))
    t = parse_text(run(TEXT, pdf))
    clean = c["fail"] == 0 and c["warn"] == 0 and t["below_minimum"] == 0
    return {"file": str(pdf), "collision": c, "text": t, "clean": clean}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="*", type=Path)
    ap.add_argument("--dir", type=Path, help="check every PDF under this directory")
    ap.add_argument("--json", type=Path, help="also write the full report here")
    args = ap.parse_args()

    targets = list(args.pdfs)
    if args.dir:
        targets += sorted(args.dir.rglob("*.pdf"))
    targets = [p for p in targets if p.is_file()]
    if not targets:
        raise SystemExit("no PDFs given; pass files or --dir")

    bad = 0
    report = []
    print(f"{'panel':<44} {'collision':<14} {'min pt':>7}  verdict")
    for pdf in targets:
        r = check(pdf)
        report.append(r)
        col = f"{r['collision']['fail']}F/{r['collision']['warn']}W"
        mn = r["text"]["minimum_pt"]
        print(f"{pdf.name:<44} {col:<14} {mn if mn is not None else '?':>7}  "
              f"{'PASS' if r['clean'] else 'FIX BEFORE DELIVERY'}")
        if not r["clean"]:
            bad += 1
            for f in r["collision"]["findings"][:6]:
                print(f"      {f[:120]}")
            if r["text"]["below_minimum"]:
                print(f"      {r['text']['below_minimum']} text run(s) below 5 pt")

    if args.json:
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nwrote {args.json}")
    print(f"\n{len(targets) - bad}/{len(targets)} clean")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
