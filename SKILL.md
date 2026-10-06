---
name: figure-guard
description: >-
  Produce manuscript figure panels as individual, audited, submission-ready files
  (PDF + PNG + editable SVG) with their source data exported for redrawing in
  Origin, GraphPad or Excel. Use for 论文配图、科研绘图、数据图、panel 拆分,
  and whenever figures will be composed by hand or sent to another agent to draw.
  Enforces a hard audit gate: no text overlap, no text crossed by a line or marker,
  legends inside the axes, minimum type size, and Times-only fonts. Not for
  interactive dashboards or statistics-only analysis.
---

# figure-guard

Draw the panels, then prove they are clean. Every rule here exists because a real
figure failed it — `references/defect-log.md` names the failure behind each one.

## When to use this

- The user wants **data figures** for a manuscript and will **compose the layout themselves**.
- The user wants the figure **source data exported** so they can redraw elsewhere.
- Figures are being **handed to another agent or person** to draw, and the rules must travel with them.
- Any figure whose labels must not collide and whose type must survive peer review.

If the user wants one finished multi-panel composition, this still applies — you just run
the compose step yourself at the end.

## The contract

Five things every delivered panel satisfies. All five are checkable, none is a matter of taste.

1. **Three formats, same stem**: `.pdf` (embedded TrueType), `.png` (600 dpi), `.svg`.
2. **SVG carries real text**, not outlines. `svg.fonttype = "none"` — an SVG is normally wanted
   *because* it is editable, and `"path"` silently destroys that. Verify by counting `<text>`
   elements in the file; a fully outlined SVG still opens fine, so "it opened" proves nothing.
3. **Source data beside the figure**, one long-format CSV per panel with a header row, plus a
   `DATA_README.md` naming every column and its unit. Write the **true values**; any offset or
   jitter used for rendering must NOT be baked into the CSV.
4. **The audit gate passes**: `0 fail, 0 warn` on collisions and `below minimum: 0` on type size.
5. **A layout map** saying which panel goes where, and at what width fraction.

## Workflow

### 1. Fix the claim before drawing

Write one sentence per panel: *what question does this panel answer?* A panel that answers two
questions is two panels. If the answer needs a number, get the number from the data first — do
not read it off a draft plot.

### 2. Load the shared style

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path("<this skill>/scripts")))
import figstyle as fs
fs.apply_style()          # Times-only, 5 pt floor, tick pads that do not graze their labels
```

Colour comes from `fs.series_color(key)`, never from a literal hex in the panel script. An
unknown key **raises** — keep it that way, it has already caught four misnamed series.

### 3. Draw one panel per file

One `fig, ax = plt.subplots(...)` per output file, sized in **millimetres** so the composed
figure lands at the journal's column width:

```python
fig, ax = plt.subplots(figsize=(86 / 25.4, 62 / 25.4))   # 86 mm single column
```

Give each panel the width it will actually occupy. If a panel is meant to run full width,
draw it full width now — compressing a 1,700-point series into half a column later destroys it.

### 4. Place text where nothing is drawn

This is where figures fail most often. The order to try, best first:

1. **Into a tick label** (`f"{lab}\n{value}"`) — cannot collide with anything.
2. **Onto a second x-label line** — empty by construction.
3. **Into the panel title's second line** — likewise.
4. **In a corner of the axes**, after opening headroom with `ax.set_ylim(...)`.
5. Last resort: `ax.annotate` with a leader line, then **move it until the audit is silent**.

Never leave a label where the audit reports it crossed. "It looks fine to me" is not the gate.

### 5. Run the gate

```bash
python scripts/check_figure.py <panel.pdf> [more.pdf ...]
```

One command, both audits, exit code 1 on anything unclean. Fix and re-run until clean.

### 6. Export the data

Long format, one row per observation, header names that state the unit
(`area_mae_pp`, `dice`, `lcc_err_pct_fg`). Add `DATA_README.md`. If a figure applies a
horizontal offset to stop points overplotting, say so in the README and keep the CSV true.

## Hard rules, with the failure each one prevents

| Rule | The failure it prevents |
|---|---|
| Count the **visible** points, not the code's `n` | Two frames differing by 0.0023 pp rendered as one dot; the "6/6 improved" claim contradicted itself on the page |
| One cleaning rule may be right for one panel and **wrong for another panel on the same data** | A frame excluded from a time axis was one of the 15 held-out frames; reusing the rule silently changed n to 14 and every mean with it |
| Report a **grid maximum**, never a fitted vertex | A parabolic fit put a peak at 1.711 where nothing was measured between 1.5 and 1.6 |
| Give an **interval and say "not localized"** when the optimum is not resolvable | A "LCC optimum r = 0.8" had 56 % bootstrap support and could not be separated from r = 1 |
| State the **model/cohort scope** of every statistic | A pooled R² of 0.056 was quoted while three of the four checkpoints were not part of the design; the formal model alone gives 0.133 |
| Keep **different n values in separate sentences** | n = 108 (one metric) and n = 340 (another) presented as one population |
| Say **Spearman ρ²** when that is what was computed | "R² = 0.133" reads as "explained 13.3 % of the variance"; a squared rank correlation is not that |
| Never compare at a chosen scale without saying so | A model looked better only at a fixed scale; at each model's own optimum they were within 0.001 |
| Carry the **padding / preprocessing mode** with every number | The same comparison moved by 0.79 Dice depending on fill mode |
| Use **Unicode superscripts**, not mathtext, for ρ² and R² in labels | Mathtext draws the exponent at ~70 % of the base size and produced a 4.34 pt run, under the 5 pt floor |
| Do not route a long-lived process through `\| Select-Object -First N` | The pipe ends after N lines and kills the process — twice |

## Reference files

- `references/plotting-requirements.md` — the full accumulated requirement list.
- `references/defect-log.md` — every defect that produced a rule above, with the number.
- `references/panel-layout.md` — the panel → position convention and a worked layout map.
- `examples/panel_template.py` — a complete, audited single-panel script to copy.

## What this skill does not do

It does not invent data, choose statistical tests, composite the final multi-panel figure,
or generate schematics and graphical abstracts. For photographic or generated illustrative
assets use a dedicated image skill.
