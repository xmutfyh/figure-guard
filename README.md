# figure-guard

Draw manuscript figure panels as **individual, audited, submission-ready files** — and prove they
are clean before delivery.

Built for a workflow where panels are **composed by hand** (or handed to another agent to draw), so
each panel ships as its own file, in three formats, with its source data beside it and a layout map
saying where it goes.

---

## The problem this solves

Figures fail in ways that are invisible to the person who drew them:

- two data points 0.0023 pp apart render as **one dot**, so a panel claiming "6/6 improved" shows five
  points and contradicts itself on the page;
- a cleaning rule that is correct for a time axis silently changes a held-out statistic from n = 15
  to n = 14, and every mean with it;
- `$R^2$` renders its exponent at ~70 % of the base size, putting a **4.34 pt** run in the PDF — under
  every journal's floor, and no visual check would catch it;
- matplotlib's `svg.fonttype` defaults to `"path"`, quietly turning an "editable" SVG into outlines
  while the file still opens perfectly;
- a label "fixed" by shortening it can make an audit go quiet **without making the panel correct**.

Every rule in this skill came from one of those. `references/defect-log.md` records all fifteen with
the numbers that exposed them.

---

## What it gives you

```
figure-guard/
├── SKILL.md                          the contract, the workflow, the hard rules
├── scripts/
│   ├── figstyle.py                   shared style: Times-only, 5 pt floor, palette,
│   │                                 legend_inside(), save() -> PDF + PNG + editable SVG
│   ├── check_figure.py               ONE command, both audits, one exit code
│   ├── audit_figure_collisions.py    text overlap / text crossed by a stroke
│   └── audit_pdf_text.py             minimum type size in the PDF
├── references/
│   ├── plotting-requirements.md      the full accumulated requirement list
│   ├── defect-log.md                 15 real defects and the rule each produced
│   └── panel-layout.md               panel -> position convention + worked layout map
├── examples/panel_template.py        a complete audited panel to copy
└── tests/test_gate.py                proves the gate passes clean and fails defective
```

---

## The gate

```bash
python scripts/check_figure.py --dir out/fig3
```

```
panel                          collision   min pt  verdict
fig3a_L1_scale_response.pdf    0F/0W          5.6  PASS
fig3c_controls.pdf             0F/0W          5.8  PASS
fig3d_optima.pdf               1F/0W          5.8  FIX BEFORE DELIVERY
      [FAIL] page 1 text-stroke: Text is crossed by 1 stroked path(s) — 'not localized'
```

**Exit code 0 only when every file is clean on both audits.** The self-test
(`python tests/test_gate.py`) proves it in both directions: it passes a clean panel, rejects a
defective one, and confirms the SVG holds real `<text>` elements rather than outlines.

---

## Requirements

```
matplotlib>=3.7
numpy>=1.24
PyMuPDF>=1.23      # only the collision audit needs it
```

The text-size audit is pure standard library.

---

## Using it with an agent

Point the agent at `SKILL.md`. The working contract is:

1. state the one question each panel answers, and get any quoted number **from the data first**;
2. draw one panel per file, **sized in millimetres** at the width it will occupy;
3. place text by preference order — tick label → second axis-label line → second title line → axis
   corner with headroom opened → leader line — and **keep moving it until the audit is silent**;
4. run the gate until `0 fail, 0 warn` and `below minimum: 0`;
5. export the **true** source values to CSV, not the rendered ones;
6. write the layout map.

Then, by hand:

- **count the visible points** on any panel making an "n of n" claim;
- check the SVGs carry real text;
- look at the figure at final size. The audit does not replace looking.

---

## Attribution

`scripts/audit_figure_collisions.py` and `scripts/audit_pdf_text.py` are taken from the
**nature-figure** skill and used here as objective gates. The rules, the defect log, the style
module and the gate wrapper come from a figure set where each of the fifteen defects actually
occurred.

## Licence

MIT for the scripts in this repository. See `LICENSE`.
