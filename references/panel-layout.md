# Panel → layout convention

When panels ship as separate files, the person composing them needs to know two things per panel:
**where it goes** and **how wide it is**. State both.

---

## Conventions worth fixing up front

| Convention | Why |
|---|---|
| Size every panel in **millimetres**, at the width it will occupy | A series drawn for half a column cannot be widened later without redrawing |
| Give the figure a **letter** and the panel a **position** (`Fig.3 (a)`, top-left) | Letters alone are ambiguous once panels are separate files |
| State the **width fraction** of the composed figure | Removes the guesswork at composition time |
| Deliver a **shared legend as its own file** when the plan calls for a single figure-level legend | Panels composed by hand cannot share one otherwise |
| Keep row heights and column widths explicit | Prevents a 60/40 split being composed as 50/50 |

## Worked example

    Fig. 3  Physical calibration and model operating scale

    ┌────────────────────────────────┬────────────────────────────────┐
    │ (a) L1 cross-condition         │ (b) L2 in-domain               │
    │     scale response             │     scale response             │
    │     50% width, 60% of height   │     50% width, 60% of height   │
    ├────────────────────────────────┼────────────────────────────────┤
    │ (c) Alternative-explanation    │ (d) Metric-dependent           │
    │     controls                   │     operating scale            │
    │     50% width, 40% of height   │     50% width, 40% of height   │
    └────────────────────────────────┴────────────────────────────────┘
              shared legend, centred above (a) and (b)

    | panel | file                     | position   | width | note                    |
    |-------|--------------------------|------------|-------|-------------------------|
    | (a)   | fig3a_L1_scale_response  | top-left   | 50%   | shares legend with (b)  |
    | (b)   | fig3b_L2_scale_response  | top-right  | 50%   | shares legend with (a)  |
    | (c)   | fig3c_controls           | bottom-left| 50%   | own small legend inside |
    | (d)   | fig3d_optima             | bottom-right| 50%  | no legend               |
    | —     | fig3_shared_legend       | above (a)(b), centred | 40% | models only |

    Full width 178 mm; total height 130–145 mm.

## A layout map is also a checklist

Writing the map exposes problems before composition:

- a panel with **no width fraction** has not been thought about;
- two panels claiming the **same cell**;
- a **legend** that is supposed to be shared but ships inside one panel;
- a width that does not divide into the target column (86 mm single, 178 mm double).

## Panel titles

Short labels, not sentences: `(a) L1 cross-condition`, not `(a) L1 cross-condition scale response
for the two formally defined models`. Anything that needs a sentence belongs in the caption.

Numbers that must be legible **on the figure** (a peak value, an n, a correlation) belong on a
second title line, a second axis-label line, or a tick label — never floating in the data region.
