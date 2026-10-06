"""Self-test: the gate must PASS a clean panel and FAIL a defective one.

A gate that has never been shown to fail is not a gate. This runs both directions and also checks
the SVG text requirement, because a fully outlined SVG opens perfectly well and would otherwise
pass unnoticed (defect D15).

    python tests/test_gate.py
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

GOOD = '''
import sys
from pathlib import Path
import numpy as np, matplotlib.pyplot as plt
sys.path.insert(0, r"{scripts}")
import figstyle as fs
fs.apply_style()
out = Path(r"{out}"); out.mkdir(parents=True, exist_ok=True)
fig, ax = plt.subplots(figsize=(86/25.4, 62/25.4))
x = np.linspace(0.6, 3.0, 12); y = 0.6 + 0.35*np.exp(-((x-1.5)**2)/0.4)
ax.plot(x, y, "-o", color=fs.series_color("M_L2"))
ax.set_xlabel("Scale factor $r$"); ax.set_ylabel("Dice")
ax.set_title("(a)  clean panel", loc="left")
fs.save(fig, out, "good", pad=0.06)
'''

BAD = '''
import sys
from pathlib import Path
import numpy as np, matplotlib.pyplot as plt
sys.path.insert(0, r"{scripts}")
import figstyle as fs
fs.apply_style()
out = Path(r"{out}"); out.mkdir(parents=True, exist_ok=True)
fig, ax = plt.subplots(figsize=(86/25.4, 62/25.4))
x = np.linspace(0.6, 3.0, 12); y = 0.6 + 0.35*np.exp(-((x-1.5)**2)/0.4)
ax.plot(x, y, "-o", color=fs.series_color("M_L2"))
ax.text(1.5, 0.80, "a label the curve runs through", fontsize=6.5)   # collision
ax.text(0.62, 0.92, r"$R^2$ = 0.133", fontsize=6.2)                  # sub-5pt mathtext exponent
ax.set_xlabel("Scale factor $r$"); ax.set_ylabel("Dice")
fs.save(fig, out, "bad", pad=0.06)
'''


def render(src: str, out: Path, name: str) -> Path:
    p = out / f"_{name}.py"
    p.write_text(src.format(scripts=SCRIPTS, out=out), encoding="utf-8")
    r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"could not render the {name} panel:\n{r.stdout}\n{r.stderr}")
    return out / f"{name}.pdf"


def gate(pdf: Path) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(SCRIPTS / "check_figure.py"), str(pdf)],
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def main() -> None:
    failures = []
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        good = render(GOOD, out, "good")
        bad = render(BAD, out, "bad")

        # 1. the clean panel must pass
        code, log = gate(good)
        if code != 0:
            failures.append(f"gate rejected a CLEAN panel:\n{log}")
        else:
            print("  [ok] clean panel passes the gate")

        # 2. the defective panel must fail, on BOTH defects
        code, log = gate(bad)
        if code == 0:
            failures.append(f"gate PASSED a defective panel:\n{log}")
        else:
            hit_collision = "text-stroke" in log or "text-text" in log
            hit_size = "below 5 pt" in log
            if not hit_collision:
                failures.append(f"gate missed the collision:\n{log}")
            if not hit_size:
                failures.append(f"gate missed the sub-5pt mathtext exponent:\n{log}")
            if hit_collision and hit_size:
                print("  [ok] defective panel rejected, both defects reported")

        # 3. the SVG must carry real text, not outlines
        svg = good.with_suffix(".svg")
        if not svg.is_file():
            failures.append("no SVG was written")
        else:
            t = svg.read_text(encoding="utf-8", errors="replace")
            n_text = len(re.findall(r"<text", t))
            if n_text == 0:
                failures.append("SVG has 0 <text> elements - labels were outlined (defect D15)")
            else:
                print(f"  [ok] SVG carries {n_text} editable text elements")

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("\nall self-tests passed")


if __name__ == "__main__":
    main()
