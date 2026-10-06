"""A complete single-panel script that passes the audit gate. Copy this and replace the data.

It demonstrates, in the order the rules matter:

  * the shared style loaded from this skill (Times-only, 5 pt floor, palette);
  * millimetre sizing at the width the panel will actually occupy;
  * a paired comparison drawn as POINTS WITH PAIRING LINES, not four bars;
  * a small fixed horizontal offset so coincident points stay countable (defect D1);
  * the mean folded INTO the tick labels, which cannot collide with anything;
  * the statistics on a second x-label line for the same reason;
  * all three output formats, with the SVG keeping real text.

Run it, then run the gate:

    python scripts/check_figure.py out/example_paired_panel.pdf
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import figstyle as fs  # noqa: E402

fs.apply_style()
OUT = Path(__file__).resolve().parent / "out"

# --- data ------------------------------------------------------------------------------------
# Replace with real per-observation values. Keep one row per observation; never pre-average.
SHOTS = ("s1", "s2", "s3", "s4", "s5", "s6")
COND_A = {"s1": 0.31, "s2": 0.46, "s3": 0.51, "s4": 0.62, "s5": 0.64, "s6": 0.88}
COND_B = {"s1": 0.49, "s2": 0.77, "s3": 0.81, "s4": 0.81, "s5": 0.86, "s6": 0.95}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # An 86 mm single-column panel. Draw it at the size it will be printed.
    fig, ax = plt.subplots(figsize=(86 / 25.4, 62 / 25.4))

    # Coincident points are separated by a fixed offset, applied to BOTH conditions so the pairing
    # lines stay correct. The exported CSV must hold the TRUE values, not these offsets.
    offs = np.linspace(-0.075, 0.075, len(SHOTS))
    for lo, s in zip(offs, SHOTS):
        ax.plot([lo, 1 + lo], [COND_A[s], COND_B[s]], "-", color="0.5", lw=0.6, zorder=3)
    ax.plot([o for o in offs], [COND_A[s] for s in SHOTS], "o", ms=3.2, mfc="white",
            mec=fs.series_color("native"), mew=0.8, zorder=5)
    ax.plot([1 + o for o in offs], [COND_B[s] for s in SHOTS], "o", ms=3.2, mfc="white",
            mec=fs.series_color("physical"), mew=0.8, zorder=5)

    ma = float(np.mean(list(COND_A.values())))
    mb = float(np.mean(list(COND_B.values())))
    ax.plot([0], [ma], "D", ms=6.4, color=fs.series_color("native"), zorder=6)
    ax.plot([1], [mb], "D", ms=6.4, color=fs.series_color("physical"), zorder=6)

    # Means go INTO the tick labels: a label there cannot be crossed by a marker or a pairing line.
    ax.set_xticks([0, 1])
    ax.set_xticklabels([f"Condition A\n{ma:.4f}", f"Condition B\n{mb:.4f}"], fontsize=6.4)

    # The headline statistic goes on a SECOND x-label line, which is empty by construction.
    improved = sum(1 for s in SHOTS if COND_B[s] > COND_A[s])
    ax.set_xlabel(f"Measurement condition\nimproved in {improved}/{len(SHOTS)} shots", fontsize=7.0)
    ax.set_ylabel("Score")
    ax.set_title("(x)  Paired comparison", loc="left")
    ax.set_xlim(-0.5, 1.5)

    fs.save(fig, OUT, "example_paired_panel", pad=0.06)
    print(f"\nwrote {OUT/'example_paired_panel.pdf'}")
    print("now run:  python scripts/check_figure.py "
          f"{OUT/'example_paired_panel.pdf'}")


if __name__ == "__main__":
    main()
