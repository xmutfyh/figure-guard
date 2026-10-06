# Plotting requirements

Accumulated from direct instruction **[U]**, from figure plans the author supplied **[P]**, and
from defects that were actually found and fixed **[D]**. The `[D]` lines are the ones worth reading
first: each cost a real rework.

---

## 1. Delivery form

| Requirement | Source |
|---|---|
| **One panel per file.** Do not deliver a pre-composited multi-panel figure unless asked. | [U] |
| **State where each panel goes** — a table of panel → figure position → width fraction. | [U] |
| Every panel in **PDF + PNG + SVG**, same stem. | [U] |
| **SVG must carry editable text**, not outlines. | [U] |
| **Source data goes beside the figure**, one folder per figure, so it can be redrawn in Origin / GraphPad / Excel. | [U] |
| Source data as **long-format CSV with a header row**, and a README naming columns and units. | [D] |

## 2. Style

| Requirement | Source |
|---|---|
| **Times only.** No substitution. | [D] |
| **Minimum type size 5 pt.** | [D] |
| **No text overlapping text, and no text crossed by a line or marker.** | [U] |
| **Legends inside the axes** — upper-left or upper-right preferred. Never outside the axes. | [U] |
| If the legend does not fit, **open headroom by extending the y limit** — do not move it outside. | [U] |
| **One palette across the whole figure set.** | [U] |
| Palette sampled from the target style rather than guessed: blue `#3870a8`, green `#48a848`, red `#d84848`, grey `#b4b4b4`; bars `#5484b4` / `#cc7878`. | [U] |
| **Keep marker shapes** (`o` / `s` / `^`) as a redundant encoding alongside colour. | [U] |
| **No enlarged halo marker** on a peak or special point. | [U] |

## 3. Panels that answer a question

| Requirement | Source |
|---|---|
| Each panel answers **one** question, stated before it is drawn. | [P] |
| Panels that share an axis definition (same x, same y, same encoding) must be **strictly isomorphic**, so the only visible difference is the effect. | [P] |
| A **control panel** exists to close off an alternative explanation, not to add a second result. | [P] |
| A **summary panel** stays a summary — do not let it become a table. | [P] |
| The **same frame / same crop / same display size** must be used for panels that are visually compared. | [P] |
| **Do not put four bars** where paired frame-level data exists — draw the points and the pairing. | [P] |
| **Do not connect non-monotone means with a line** — it implies a trend the data does not have. | [P] |
| **Do not hide the sample size** behind an aggregate. Show raw points with the mean. | [P] |
| Image panels that claim a change must show **the same overlay on both**, so the reader compares once. | [P] |

## 4. Statistics and wording

| Requirement | Source |
|---|---|
| Report a **grid maximum**, never a fitted vertex. | [P] |
| When an optimum is not resolvable, report the **interval** and label it **not localized** — do not give a point value. | [D] |
| Say **Spearman ρ / ρ²** when a rank correlation was computed. Do not write "R²" or "explained X % of variance". | [P] |
| **Keep different n in separate statements.** Do not present a 108-point subset and a 340-point set as one population. | [P] |
| A rule that cleans a time axis may be **wrong** for a held-out statistic on the same data. State which rule applies to which panel. | [D] |
| Every performance number carries its **preprocessing / padding mode**. | [D] |
| State the **scope** of any pooled statistic — which models, which cohorts. A pooled number can understate the very effect it describes. | [D] |
| Never compare at a **chosen** operating point without saying that is what was done. | [D] |
| Do not upgrade a claim beyond what the protocol supports; keep the protocol in the sentence. | [P] |

## 5. Before delivery

1. **Count the visible points** on every panel that makes an "all n improved" or "n of n" claim.
2. Run `scripts/check_figure.py` on every PDF and get `0 fail, 0 warn` and `below minimum: 0`.
3. Re-open at final size and look at it. The audit does not replace looking.
4. Check the SVGs have real `<text>` elements.
5. Confirm the exported CSVs hold the **true** values, not the rendered ones.
6. Write the layout map.
