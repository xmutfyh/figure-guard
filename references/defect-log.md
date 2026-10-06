# Defect log

Every defect below was found in a real figure set and fixed. Each one produced a rule. They are
recorded with the number that exposed them, because a rule without its failure gets ignored.

---

## D1 — Two frames differing by 0.0023 pp rendered as a single dot

A paired panel claimed **6/6 frames improved**. Two of the six had native-scale errors of 8.6400 and
8.6424 pp. On a 0–16 pp axis that is 0.014 % of the axis height — one dot, not two. The panel showed
five points, so the figure **contradicted its own claim on the page**.

Found by: the author counting the dots and asking "does this only have five points?"
The audit had passed the panel, twice.

**Rule**: count the visible points on every panel with an "n of n" claim. A gap under ~1 % of the
axis range is one point at render time. The fix is a small fixed horizontal offset per series member,
applied identically wherever that member appears — the pairing lines stay honest and the CSV keeps
the true values.

The same defect was then found in a **second** figure, in two of its four conditions (gaps 0.0003 and
0.0048 Dice). Check every paired panel, not just the one that was questioned.

---

## D2 — A cleaning rule applied to the wrong panel

A time-axis panel correctly excluded an isolated blank reference frame captured 195 minutes before
the sequence began — plotted on a time axis it draws two meaningless straight lines.

The **same frame was one of 15 held-out Human Gold frames**. Applying the same exclusion to the
held-out error panel silently changed n from 15 to 14, and every mean with it:

| | n = 14 (wrong) | n = 15 (correct) | published |
|---|---|---|---|
| model | 0.0221 | **0.0228** | 0.0228 |
| fixed threshold | 0.3027 | **0.5493** | 0.5493 |
| Otsu | 1.7276 | **2.3521** | 2.3521 |

**Rule**: a data-cleaning rule is scoped to the panel that needs it. Before reusing one, check whether
the excluded records belong to the other panel's population. The figure script now passes the *full*
row list to the held-out panel and the *cleaned* list to the time-axis panel, with a comment on each.

---

## D3 — A fitted vertex reported as a measurement

An optima table stored both the grid maximum (`argmax_r`) and a parabolic vertex fitted in log r
(`optimum_r`). For one model they were **1.5** and **1.711**, with no measurement between r = 1.5 and
r = 1.6. The fitted value reads as a measurement and is not one.

**Rule**: report grid maxima. If a fit is also stored, label which is which and never plot the fit as
the optimum.

---

## D4 — An optimum reported that the data cannot locate

A metric's grid minimum sat at r = 0.8, on the far side of the physical scale from the other model's.
Bootstrapping over the 6 frames put **r = 1 inside the central 50 %** of the optimum location, and
only 56 % of replicates chose r = 0.8 at all; the rest scattered to 0.9, 1.4, 1.5, 2.0, 2.2.

For symmetry the same test was run on the other model's three metrics — **all three resolved**, so
this was not a stricter standard applied to one model.

**Rule**: bootstrap the argmax over the replication unit (frames, not grid points) and report the
central interval. If the reference value falls inside it, draw a **range** and label it
**not localized**. A point value there is a sampling artefact presented as a model property.

---

## D5 — A pooled statistic that understated its own effect

A correlation was quoted over "1,468 real predictions" from four checkpoints. Three of the four were
historical arms with no definition in the manuscript's Methods or model table.

Re-derived on the formally defined model alone:

| metric | pooled | formal model only |
|---|---|---|
| normalized LCC error | n = 1360, ρ² = 0.0556 | **n = 340, ρ² = 0.1333** |
| LCC error (unnormalized) | n = 1468, ρ² = 0.0521 | n = 448, ρ² = 0.1199 |

The pooled number was **2.4× weaker** than the effect it was describing.

**Rule**: state the model and cohort scope of every statistic, and recompute rather than reuse a
pooled figure when the population changes.

---

## D6 — Two different n presented as one population

A fragmentation correlation used a 108-prediction subset; the LCC correlation used 340. Both are
legitimate, but presented together they read as one population.

**Rule**: keep n = 108 and n = 340 in separate statements, and never in one sentence without saying
which belongs to which metric.

---

## D7 — "R²" for a squared rank correlation

`ρ² = 0.133` was printed as `R² = 0.133`. A squared rank correlation is **not** a fraction of
variance explained, and the label invites that reading.

**Rule**: print `Spearman ρ = −0.365, ρ² = 0.133`. Reserve "R²" for a regression.

---

## D8 — Mathtext superscript under the type floor

`$R^2$` renders the exponent at roughly 70 % of the base size. At a 6.2 pt base that is a **4.34 pt**
run in the PDF, below the 5 pt floor, and no visual check would have caught it.

**Rule**: use Unicode superscripts (`ρ²`, `R²`) in labels. Audit every PDF for the minimum type size.

---

## D9 — A comparison at one model's favourable operating point

Two models were compared at a **fixed** scale, where one led by 0.1485 Dice. At **each model's own
best scale** they were within **0.0011** of each other.

**Rule**: if a comparison uses a chosen operating point, say so, and report the each-model-optimum
version alongside. The honest claim here was narrower and stronger: the model was usable *at the
physically meaningful scale*, not better in general.

---

## D10 — A figure that showed the same data three times

A conditional-spread panel read a summary file holding **three scopes × six bins = 18 rows** and
plotted all of them: the same distribution three times over, 18 columns wide, tick labels running
together.

**The collision audit passed it.** The label overlap had been "fixed" earlier by shortening the
labels — which made the audit quiet without making the panel right.

**Rule**: when a plot looks crowded, ask **why there are so many columns** before adjusting the
labels. Optimising for a passing audit is not the same as being correct. Also assert a minimum
number of expected groups so a mis-filtered read fails loudly.

---

## D11 — A scale constant reused in the wrong cohort

A counterexample panel resampled an **L2** frame using the **L1** native ratio (0.2722). The correct
factor for an L2 frame is `1.0 / r`. With the wrong constant the reproduced Dice were 0.8177 / 0.5574
against published values of 0.9067 / 0.9104.

**Rule**: a constant that encodes a scale must not be reused at another scale. Check the cohort of
every frame before applying a ratio, and assert the recomputed metric matches the published one
before drawing anything from it.

---

## D12 — A substring match that silently selected the wrong pair

A counterexample table holds **ten** pairs on the same frame. Selecting on the substring `"0.7"`
picked a different model pair and returned Dice 0.9386 / LCC 1.317 instead of 0.9104 / 0.434.

**Rule**: match on the exact setting identifiers. When a candidate set has more than one plausible
member, assert the count and print the chosen row.

---

## D13 — Ratio rewards a tiny denominator

A matched-pair counterexample was first chosen by **maximising the ratio** of two error values. The
winner had a denominator of **0.09 %** of the reference area — almost any difference looks large
against it.

Ranking instead on the **absolute** difference selected a pair separated by **37.7 percentage
points** (against 3.1 for the ratio winner) and with a **smaller** Dice gap (0.0060 against 0.0092).

**Rule**: rank counterexamples on the absolute scientific difference; report the ratio, if at all,
as secondary small text.

---

## D14 — A pipe that killed the process it was monitoring

`... | Select-Object -First 3` terminates the pipeline after three lines, which **kills the process
on the other end**. Used to "check the arguments" of a training script it started the training; used
to launch a watcher it would have killed the watcher ten minutes later, leaving a multi-hour job with
nothing to evaluate it.

Made twice, both times on a long-lived process.

**Rule**: never route a long-lived or monitored process through an output-limiting pipe. Launch it
detached with output redirected to a file.

---

## D15 — Silent default that turned an editable SVG into outlines

Matplotlib's `svg.fonttype` defaults to `"path"`, which converts every label to outlines. A figure
script that set its own rcParams (and so did not inherit the shared style) produced an SVG with
**0 `<text>` elements and 140 `<path>`** — completely uneditable — while its own comment claimed
"text stays editable". The file opened fine.

**Rule**: every script that sets its own rcParams must set `svg.fonttype` itself. Verify by counting
`<text>` elements in the output, not by opening the file.
