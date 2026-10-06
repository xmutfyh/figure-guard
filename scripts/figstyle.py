"""Shared figure style and the legend-placement helper, validated once and reused.

WHY A MODULE
------------
Two defects were found by audit rather than by eye while making Fig. 6 (see `README.md`): a legend
that landed on top of bar patches because the helper only inspected `ax.get_lines()`, and a second
typeface embedded through mathtext's DejaVu default. Both fixes belong in ONE place from now on,
so every subsequent figure inherits them instead of re-deriving them.

The user's constraints, encoded here:
  * Times-family serif for BOTH prose text and mathematics;
  * legends inside the axes, upper-left or upper-right, never outside;
  * when the data would reach into the legend band, the Y-AXIS IS EXTENDED so the data stops below
    the legend - the explicit fallback the user asked for.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# one restrained palette: one neutral family, one signal family, one accent
NEUTRAL = {"M_L2": "#1f4e79", "S0": "#2e75b6", "S1": "#8faadc", "B1": "#4a7ebb"}
CONTROL = "0.45"
ACCENT = "#c00000"
SIGNAL = "#2e75b6"
MUTED = "#bfbfbf"

RC = {
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "Nimbus Roman", "DejaVu Serif"],
    # mathtext defaults to DejaVu, which silently embeds a SECOND typeface beside Times
    "mathtext.fontset": "custom",
    "mathtext.rm": "Times New Roman",
    "mathtext.it": "Times New Roman:italic",
    "mathtext.bf": "Times New Roman:bold",
    "mathtext.default": "it",
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8.5,
    "xtick.labelsize": 7.2,
    "ytick.labelsize": 7.2,
    "legend.fontsize": 6.8,
    "axes.linewidth": 0.7,
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "xtick.major.size": 2.6,
    "ytick.major.size": 2.6,
    # tick marks and their labels just touch at the default pad, which the collision audit reports as
    # a text crossed by a stroked path (found on the leading '0' of Fig. 9 panel a)
    "xtick.major.pad": 3.4,
    "ytick.major.pad": 3.0,
    "lines.linewidth": 1.2,
    "lines.markersize": 3.2,
    "pdf.fonttype": 42,          # embed as TrueType so text stays editable
    "ps.fonttype": 42,
    # SVG keeps real text, not outlines: an SVG is normally wanted so the figure can be edited, and
    # `path` would turn every label into a shape and destroy that. The trade-off is that the font is
    # referenced by name, so a viewer without Times will substitute it - see the note in `save`.
    "svg.fonttype": "none",
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
}


def apply_style() -> None:
    plt.rcParams.update(RC)


# ---------------------------------------------------------------------------------------------
# Unified series palette for Paper 1
# ---------------------------------------------------------------------------------------------
# Sampled from the author's reference figure rather than estimated: the green line lands on
# #48a848, the blue on #3870a8 and the red on #d84848; the bar pair is #5484b4 / #cc7878.
#
# Colour identifies a ROLE, so a hue is reused across figures only where the two series never
# appear together:
#   blue    the reference / single-source model (M_L2)
#   green   the second model or alternative branch (M_MS in Fig.4-5, B1 in Fig.3, case B in Fig.6)
#   red     the failure or high-error role (S0 in Fig.3, Fixed T=80 in Fig.5, case A in Fig.6)
#   grey    the training-free threshold reference (Otsu)
# Markers (o / s / ^) stay as they were: shape and colour are redundant encodings here.
PALETTE = {
    "blue": "#3870a8",
    "green": "#48a848",
    "red": "#d84848",
    "light_blue": "#5484b4",
    "light_red": "#cc7878",
    "grey": "#b4b4b4",
    "ink": "0.15",
}
SERIES = {
    "M_L2": PALETTE["blue"],
    "M_MS": PALETTE["green"],
    "S0": PALETTE["red"],
    "B1": PALETTE["green"],
    "S1": PALETTE["green"],
    "fixed80": PALETTE["red"],
    "otsu": PALETTE["grey"],
    "case_a": PALETTE["red"],
    "case_b": PALETTE["green"],
    "native": PALETTE["light_blue"],
    "physical": PALETTE["light_red"],
}


def series_color(key: str) -> str:
    """Colour for a series key, failing loudly rather than silently defaulting."""
    if key not in SERIES:
        raise KeyError(f"no palette entry for {key!r}; known keys: {sorted(SERIES)}")
    return SERIES[key]


def legend_inside(ax, loc: str = "upper right", pad_frac: float = 0.075, **kw):
    """Place a legend INSIDE the axes, extending the y-axis if the data would collide with it.

    Measures rather than guesses:
      1. draw the legend and measure its height in axes-fraction units;
      2. find the top (for an UPPER legend) or the bottom (for a LOWER legend) of every drawn data
         artist inside the legend's horizontal span - lines, bar patches AND scatter collections;
      3. if the data would enter the legend band, extend the y-axis on THAT side so the data stops
         clear of it.

    The x-limits are never touched, so the reader's sense of the x-range is preserved.

    TWO DEFECTS THIS FUNCTION HAS ALREADY HAD, both caught by the collision audit:
      * it inspected only `ax.get_lines()`, so in a bar panel the legend landed on the bars;
      * it always extended the TOP of the y-axis, which does nothing for a legend in a lower corner
        whose risk is data pressing up from below. A `lower left` legend in Fig. 9 sat on a data
        point for exactly this reason.
    """
    leg = ax.legend(loc=loc, frameon=True, framealpha=1.0, borderpad=0.32,
                    handlelength=1.5, handletextpad=0.45, labelspacing=0.28,
                    edgecolor="0.75", **kw)
    fig = ax.figure
    fig.canvas.draw()
    bb = leg.get_window_extent().transformed(ax.transAxes.inverted())
    band = (bb.y1 - bb.y0) + pad_frac
    if band >= 0.85:                       # legend taller than the axes: nothing to expand into
        return leg
    upper = "upper" in loc

    x0, x1 = ax.get_xlim()
    logx = ax.get_xscale() == "log"
    lo, hi = (np.log10(x0), np.log10(x1)) if logx else (x0, x1)
    cut = lo + bb.x0 * (hi - lo)

    vals: list[float] = []
    for line in ax.get_lines():
        # `axhline` / `axvline` use a BLENDED transform, so their get_ydata() is in AXES fraction
        # (0..1), not data units. Reading it as data dragged panel b's y-axis down to -0.5 in Fig. 9.
        # Only artists drawn in plain data coordinates may inform the y-limit.
        if line.get_transform() is not ax.transData:
            continue
        xd = np.asarray(line.get_xdata(), dtype=float)
        yd = np.asarray(line.get_ydata(), dtype=float)
        if xd.size == 0:
            continue
        xs = np.log10(np.abs(xd)) if logx else xd
        m = np.isfinite(xs) & np.isfinite(yd) & (xs >= cut)
        if m.any():
            vals.append(float(np.nanmax(yd[m])) if upper else float(np.nanmin(yd[m])))
    for patch in ax.patches:
        if patch.get_transform() is not ax.transData:
            continue
        xd = float(patch.get_x())
        right = xd + float(patch.get_width())
        xs = np.log10(max(right, 1e-12)) if logx else right
        xl = np.log10(max(xd, 1e-12)) if logx else xd
        if xs >= cut or xl >= cut:
            h = float(patch.get_height())
            vals.append(h if upper else min(0.0, h))
    for coll in ax.collections:
        # A `fill_between` band is a PolyCollection whose vertices live in get_paths(), NOT in
        # get_offsets(); get_offsets() returns an empty array. Reading only offsets therefore
        # skipped every error band, and the legend in Fig. 9 panel a ended up sitting on the edge
        # of the bands even though the helper thought it had made room.
        ys: list[float] = []
        try:
            off = np.asarray(coll.get_offsets(), dtype=float)
            if off.ndim == 2 and off.shape[1] >= 2 and off.size:
                xs = np.log10(np.abs(off[:, 0])) if logx else off[:, 0]
                m = np.isfinite(xs) & (xs >= cut)
                if m.any():
                    ys.extend(off[m, 1].tolist())
        except Exception:                                          # noqa: BLE001
            pass
        if not ys:
            for path in coll.get_paths():
                v = np.asarray(path.vertices, dtype=float)
                if v.ndim != 2 or v.shape[1] < 2 or not v.size:
                    continue
                xs = np.log10(np.abs(v[:, 0])) if logx else v[:, 0]
                m = np.isfinite(xs) & np.isfinite(v[:, 1]) & (xs >= cut)
                if m.any():
                    ys.extend(v[m, 1].tolist())
        ys = [y for y in ys if np.isfinite(y)]
        if ys:
            vals.append(max(ys) if upper else min(ys))
    if not vals:
        return leg

    # Adjust, re-measure, adjust once more. Changing ylim changes the legend's height in axes
    # fraction (its font is fixed but the axes data range is not), so a single pass can land just
    # short - which is what left Fig. 9 panel a's legend touching the error bands.
    for _ in range(2):
        y_lo, y_hi = ax.get_ylim()
        extreme = max(vals) if upper else min(vals)
        frac = (extreme - y_lo) / (y_hi - y_lo)
        if upper:
            target = 1.0 - band - 0.02
            if frac <= target:
                break
            ax.set_ylim(y_lo, y_lo + (extreme - y_lo) / max(target, 0.05))
        else:
            target = band + 0.02
            if frac >= target:
                break
            ax.set_ylim(y_hi - (y_hi - extreme) / max(1.0 - target, 0.05), y_hi)
        fig.canvas.draw()
        bb = leg.get_window_extent().transformed(ax.transAxes.inverted())
        band = (bb.y1 - bb.y0) + pad_frac
    fig.canvas.draw()
    return leg


def save(fig, out_dir, stem: str, formats=(("pdf", None), ("png", 600), ("svg", None)),
         pad: float | None = None) -> None:
    """Write every requested format.

    `pad` overrides `savefig.pad_inches` for this call. The default (0.02 in) is right for figures
    whose outermost ink is a tick label, but a figure that carries an annotation outside the axes -
    a group label under the x axis, for instance - can end up with that text flush against the page
    edge, which the collision audit reports as `text-page-clipping`. Pass a larger `pad` there.

    SVG is included because the manuscript figures are also wanted as editable vector files. It is
    the one format whose TEXT is not self-contained: with `svg.fonttype = "none"` the labels stay
    real text (editable, searchable) but the font is only named, so a viewer without Times
    substitutes it. If a submission system must render identically everywhere, set
    `svg.fonttype = "path"` before calling this and the glyphs become outlines - at the cost of
    editability. The `.pdf` keeps embedded TrueType (`pdf.fonttype = 42`) and stays correct either
    way.
    """
    from pathlib import Path
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # `bbox_inches` is passed EXPLICITLY, not inherited from rcParams. Passing only `pad_inches`
    # while relying on `savefig.bbox` had no effect on the page box, and multi-line tick labels kept
    # running past the page edge (reported as text-page-clipping on five labels of one panel).
    kw = {"bbox_inches": "tight"}
    if pad is not None:
        kw["pad_inches"] = pad
    for ext, dpi in formats:
        p = out_dir / f"{stem}.{ext}"
        fig.savefig(p, dpi=dpi, **kw)
        print(f"wrote {p}")
    plt.close(fig)

