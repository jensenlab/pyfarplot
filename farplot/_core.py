"""
Factor-and-response plots (farplots).

A farplot shows a continuous response variable alongside the corresponding
factor settings from a designed experiment. The response is displayed as a
scatter plot; below it, each factor is shown as a row in a heatmap-style grid
where each column is one (unique) treatment. Cells are square for clean,
publication-quality output.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_sign(val):
    """Convert a factor value to -1, 0, or 1 following doetools conventions."""
    if isinstance(val, (int, float, np.integer, np.floating)):
        v = float(val)
        if v < 0:
            return -1
        if v > 0:
            return 1
        return 0
    s = str(val).strip()
    if s in ("-1", "-"):
        return -1
    if s in ("1", "+1", "+"):
        return 1
    return 0


def _abbreviate(levels, n_chars):
    """Abbreviate strings to n_chars, appending a counter when duplicates arise."""
    prefixes = [str(lv)[:n_chars] for lv in levels]
    counts = {}
    for p in prefixes:
        counts[p] = counts.get(p, 0) + 1
    seen = {}
    result = []
    for p in prefixes:
        if counts[p] > 1:
            seen[p] = seen.get(p, 0) + 1
            result.append(f"{p}{seen[p]}")
        else:
            result.append(p)
    return result


def _make_norm(vmin, vmax, vcenter=0.0):
    """TwoSlopeNorm when values span zero, plain Normalize otherwise."""
    if vmin < vcenter < vmax:
        return mcolors.TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    return mcolors.Normalize(vmin=vmin, vmax=vmax)


def guess_factor_type(series):
    """
    Infer the display type for a single factor column.

    Returns 'sign' for numeric columns whose values are a subset of {-1, 0, 1},
    'continuous' for other numeric columns, and 'factor' for everything else.
    """
    if pd.api.types.is_numeric_dtype(series):
        unique = set(series.dropna().unique())
        if unique <= {-1, 0, 1, -1.0, 0.0, 1.0}:
            return "sign"
        return "continuous"
    return "factor"


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def farplot(
    data,
    response,
    factors=None,
    factor_type=None,
    # factor appearance — symbol mode
    factor_colors=("red", "gray", "black"),
    factor_fills=("red", "white", "black"),
    color_signs=True,
    label_chars=2,
    factor_size=None,
    zero_size=0.1,
    size_transform="sqrt",
    normalize="all",
    # factor appearance — heatmap mode
    cell_style="symbol",
    cmap="RdBu_r",
    show_key=False,
    # response / ordering
    order_response=True,
    stack_replicates=True,
    stat="mean",
    show_stat=None,
    response_color="orange",
    response_marker="o",
    stat_color="black",
    # layout
    cell_size=0.45,
    response_height=2.5,
    show_grid=False,
    clean_axes=False,
    ylim=None,
    figsize=None,
    # output
    savefig=None,
    dpi=150,
):
    """
    Create a factor-and-response (farplot) visualization.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame with factor columns and a response column.
    response : str
        Name of the response column in *data*.
    factors : list of str, optional
        Factor columns to display. Default: all columns except *response*.
    factor_type : str, list, or dict, optional
        Display type for each factor – ``'sign'``, ``'continuous'``, or
        ``'factor'``. A single string applies to all factors. A list must
        match the order of *factors*. Default: auto-detected.
    factor_colors : tuple of str
        (negative, zero, positive) outline/text colors for symbol mode.
        Default: ``('red', 'gray', 'black')``.
    factor_fills : tuple of str
        (negative, zero, positive) fill colors for continuous symbols in
        symbol mode. Default: ``('red', 'white', 'black')``.
    color_signs : bool
        Color ``+``/``0``/``−`` characters by sign in symbol mode.
        Default: True.
    label_chars : int
        Characters used to abbreviate categorical factor levels. Default: 2.
    factor_size : float, optional
        Maximum scatter marker area (points²) for continuous symbols in
        symbol mode. Default: auto-sized to fit within a cell.
    zero_size : float
        Relative size (0–1) of continuous zero markers in symbol mode.
        Default: 0.1.
    size_transform : {'sqrt', None} or callable
        Transform applied to scaled continuous values before sizing in symbol
        mode. ``'sqrt'`` makes symbol *area* proportional to factor level.
        Default: ``'sqrt'``.
    normalize : {'all', 'row'}
        Normalization scope for continuous factors. ``'all'`` scales against
        the global maximum across all continuous factors (default). ``'row'``
        scales each factor independently.
    cell_style : {'symbol', 'heatmap'}
        How factor cells are rendered. ``'symbol'`` (default) draws ``+``/
        ``−`` text and sized circles. ``'heatmap'`` fills each cell with a
        color from *cmap* — diverging from white at zero through saturated
        colors at the extremes. Categorical (``'factor'``) columns always use
        text labels regardless of this setting.
    cmap : str or Colormap
        Colormap used in ``cell_style='heatmap'`` mode. A diverging colormap
        (e.g. ``'RdBu_r'``, ``'PiYG'``) works well when factor values span
        both negative and positive. For purely positive factors a sequential
        map such as ``'Blues'`` is a good choice. Default: ``'RdBu_r'``.
    show_key : bool
        Draw a horizontal colorbar below the factor grid (only meaningful
        when ``cell_style='heatmap'``). Default: False.
    order_response : bool
        Sort treatments by the response statistic. Default: True.
    stack_replicates : bool
        Collapse runs with identical factor settings. Default: True.
    stat : str or callable
        Statistic for ordering and the replicate summary line.
        Accepts ``'mean'``, ``'median'``, ``'min'``, ``'max'``, or a
        callable. Default: ``'mean'``.
    show_stat : bool, optional
        Show a horizontal tick for the replicate statistic. Default: True
        when replicates are stacked, False otherwise.
    response_color : str
        Color of response scatter points. Default: ``'orange'``.
    response_marker : str
        Matplotlib marker style for response points. Default: ``'o'``.
    stat_color : str
        Color of the replicate-statistic tick. Default: ``'black'``.
    cell_size : float
        Width and height of each factor-grid cell in inches. Default: 0.45.
    response_height : float
        Height of the response panel in inches. Default: 2.5.
    show_grid : bool
        Draw cell border lines in the factor grid. Default: False.
    clean_axes : bool
        Remove the top and right spines from the response panel for a
        minimal, publication-ready look. Default: False.
    ylim : tuple of (float, float), optional
        ``(ymin, ymax)`` limits for the response axis. Default: auto-scaled
        with a small margin around the data.
    figsize : tuple, optional
        ``(width, height)`` in inches. Default: auto-computed from *cell_size*.
    savefig : str or list of str, optional
        Filename(s) to save. Supports ``.svg``, ``.pdf``, ``.png``.
    dpi : int
        Dots-per-inch for raster output. Default: 150.

    Returns
    -------
    matplotlib.figure.Figure
    """
    # ------------------------------------------------------------------ data
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    if response not in data.columns:
        raise ValueError(f"response column '{response}' not found in data")

    y_raw = data[response].values.astype(float)

    if factors is None:
        factor_cols = [c for c in data.columns if c != response]
    else:
        factor_cols = list(factors)
    if not factor_cols:
        raise ValueError("No factor columns found")

    X = data[factor_cols].reset_index(drop=True)
    n_factors = len(factor_cols)

    # --------------------------------------------------------- factor types
    if factor_type is None:
        ftypes = {c: guess_factor_type(X[c]) for c in factor_cols}
    elif isinstance(factor_type, str):
        ftypes = {c: factor_type for c in factor_cols}
    elif isinstance(factor_type, (list, tuple)):
        if len(factor_type) != n_factors:
            raise ValueError("factor_type length must match number of factors")
        ftypes = dict(zip(factor_cols, factor_type))
    else:
        ftypes = dict(factor_type)

    # ---------------------------------------------------------- stat / size
    _stat_map = {"mean": np.mean, "median": np.median, "min": np.min, "max": np.max}
    stat_fn = _stat_map.get(stat, stat) if isinstance(stat, str) else stat

    if size_transform == "sqrt":
        size_fn = np.sqrt
    elif size_transform is None:
        size_fn = lambda x: x  # noqa: E731
    else:
        size_fn = size_transform

    # ------------------------------------------------------- stack reps
    if stack_replicates:
        X_str = X.astype(str)
        seen: dict = {}
        group_rows: list = []
        first_rows: list = []
        for i in range(len(X)):
            key = tuple(X_str.iloc[i])
            if key not in seen:
                seen[key] = len(first_rows)
                first_rows.append(i)
                group_rows.append([i])
            else:
                group_rows[seen[key]].append(i)
        X_unique = X.iloc[first_rows].reset_index(drop=True)
        y_groups = [y_raw[rows] for rows in group_rows]
        has_reps = any(len(g) > 1 for g in y_groups)
    else:
        X_unique = X.copy()
        y_groups = [np.array([v]) for v in y_raw]
        has_reps = False

    n_cols = len(y_groups)

    if show_stat is None:
        show_stat = has_reps

    # --------------------------------------------------- sort by response
    y_stats = np.array([stat_fn(g) for g in y_groups])
    if order_response:
        order = np.argsort(y_stats)
        X_plot = X_unique.iloc[order].reset_index(drop=True)
        y_groups_plot = [y_groups[i] for i in order]
        y_stats_plot = y_stats[order]
    else:
        X_plot = X_unique
        y_groups_plot = y_groups
        y_stats_plot = y_stats

    # ----------------------------------------- global max for continuous
    global_max = 0.0
    for col in factor_cols:
        if ftypes[col] == "continuous":
            vals = pd.to_numeric(X_plot[col], errors="coerce").abs()
            m = float(vals.max())
            if np.isfinite(m):
                global_max = max(global_max, m)
    if global_max < 1e-10:
        global_max = 1.0

    # ------------------------------------------ key panel sizing (pre-layout)
    if show_key and cell_style == "heatmap":
        _key_gap_r = 0.06                           # gap right of factor grid
        _key_panel_w = max(6.0 * cell_size, 0.9)   # key panel width in inches
    else:
        _key_gap_r = 0.0
        _key_panel_w = 0.0

    # ------------------------------------------------------ figure layout
    cell = cell_size          # inches per cell
    left_pad = 1.5            # room for factor labels
    right_pad = 0.35 + (_key_gap_r + _key_panel_w if (show_key and cell_style == "heatmap") else 0)
    top_pad = 0.25
    bot_pad = 0.30
    vgap = 0.06               # gap between panels

    grid_w = n_cols * cell
    grid_h = n_factors * cell

    if figsize is None:
        fw = left_pad + grid_w + right_pad
        fh = top_pad + response_height + vgap + grid_h + bot_pad
    else:
        fw, fh = figsize

    fig = plt.figure(figsize=(fw, fh))

    # Factor grid: exact size so each data unit = cell inches → square cells
    ax_f = fig.add_axes([
        left_pad / fw,
        bot_pad / fh,
        grid_w / fw,
        grid_h / fh,
    ])

    # Response panel directly above the grid
    ax_r = fig.add_axes([
        left_pad / fw,
        (bot_pad + grid_h + vgap) / fh,
        grid_w / fw,
        response_height / fh,
    ])

    # ----------------------------------------------- symbol size defaults
    cell_pts = cell * 72.0    # cell size in typographic points
    if factor_size is None:
        d_pts = cell_pts * 0.75
        factor_size = np.pi * (d_pts / 2) ** 2

    response_s = np.pi * (cell_pts * 0.20) ** 2
    sign_fontsize = cell_pts * 0.55

    # ================================================== response panel
    x_pos = np.arange(1, n_cols + 1, dtype=float)

    for xi, grp in zip(x_pos, y_groups_plot):
        ax_r.scatter(
            np.full(len(grp), xi), grp,
            c=response_color,
            s=response_s,
            marker=response_marker,
            zorder=3,
            linewidths=0,
            clip_on=False,
        )

    if show_stat:
        hw = 0.28
        for xi, ys in zip(x_pos, y_stats_plot):
            ax_r.plot(
                [xi - hw, xi + hw], [ys, ys],
                color=stat_color,
                linewidth=1.5,
                solid_capstyle="butt",
                zorder=4,
            )

    y_all = np.concatenate(y_groups_plot)
    yrange = y_all.max() - y_all.min() if y_all.max() != y_all.min() else 1.0
    margin = yrange * 0.08
    if ylim is not None:
        ax_r.set_ylim(ylim)
    else:
        ax_r.set_ylim(y_all.min() - margin, y_all.max() + margin)
    ax_r.set_xlim(0.5, n_cols + 0.5)
    ax_r.set_ylabel(response, fontsize=10)
    ax_r.tick_params(axis="x", bottom=False, labelbottom=False)
    ax_r.tick_params(axis="y", labelsize=8)
    ax_r.spines["bottom"].set_visible(False)

    if clean_axes:
        ax_r.spines["top"].set_visible(False)
        ax_r.spines["right"].set_visible(False)

    # ================================================== factor grid
    ax_f.set_xlim(0.5, n_cols + 0.5)
    ax_f.set_ylim(0.0, n_factors)

    tick_ys = np.arange(n_factors) + 0.5
    ax_f.set_yticks(tick_ys)
    ax_f.set_yticklabels(factor_cols[::-1], fontsize=9)
    ax_f.tick_params(axis="y", length=0, pad=3)
    ax_f.set_xticks([])

    if show_grid:
        lw = 0.5
        for xb in np.arange(0.5, n_cols + 1.0, 1.0):
            ax_f.axvline(xb, color="black", linewidth=lw, zorder=3)
        for yb in np.arange(0.0, n_factors + 1.0, 1.0):
            ax_f.axhline(yb, color="black", linewidth=lw, zorder=3)

    # ----------------------------------------- heatmap colormap setup
    _default_cmap_name = "RdBu_r"
    def _get_cmap(col):
        if not isinstance(cmap, dict):
            src = cmap
        else:
            src = cmap.get(col, cmap.get("default", _default_cmap_name))
        return plt.get_cmap(src) if isinstance(src, str) else src

    # ------------------------------------------------- per-factor rows
    for fi, col in enumerate(factor_cols):
        row_y = n_factors - fi - 0.5
        ftype = ftypes[col]
        _cmap = _get_cmap(col) if cell_style == "heatmap" else None

        # ---- heatmap rendering (sign + continuous only) ----
        if cell_style == "heatmap" and ftype in ("sign", "continuous"):
            if ftype == "sign":
                norm = _make_norm(-1.0, 1.0)
                for xi, x in enumerate(x_pos):
                    s = _to_sign(X_plot[col].iloc[xi])
                    color = _cmap(norm(float(s)))
                    rect = mpatches.Rectangle(
                        (x - 0.5, row_y - 0.5), 1.0, 1.0,
                        facecolor=color, edgecolor="none", zorder=2,
                    )
                    ax_f.add_patch(rect)

            else:  # continuous
                vals = pd.to_numeric(X_plot[col], errors="coerce").values.astype(float)
                col_max = global_max if normalize == "all" else max(np.nanmax(np.abs(vals)), 1e-10)
                norm = _make_norm(-col_max, col_max)
                for xi, (x, val) in enumerate(zip(x_pos, vals)):
                    color = _cmap(norm(val))
                    rect = mpatches.Rectangle(
                        (x - 0.5, row_y - 0.5), 1.0, 1.0,
                        facecolor=color, edgecolor="none", zorder=2,
                    )
                    ax_f.add_patch(rect)

        # ---- symbol rendering ----
        elif ftype == "sign":
            for xi, x in enumerate(x_pos):
                s = _to_sign(X_plot[col].iloc[xi])
                char = {-1: "−", 0: "0", 1: "+"}[s]
                color = factor_colors[s + 1] if color_signs else "black"
                ax_f.text(
                    x, row_y, char,
                    ha="center", va="center",
                    fontsize=sign_fontsize,
                    fontweight="bold",
                    color=color,
                    clip_on=True,
                )

        elif ftype == "continuous":
            vals = pd.to_numeric(X_plot[col], errors="coerce").values.astype(float)
            col_max = global_max if normalize == "all" else max(np.nanmax(np.abs(vals)), 1e-10)

            for xi, (x, val) in enumerate(zip(x_pos, vals)):
                s = int(np.sign(val))
                if abs(val) < 1e-10:
                    s = 0
                    rel = zero_size
                else:
                    rel = abs(val) / col_max
                sz = size_fn(max(rel, 0.0)) * factor_size

                ax_f.scatter(
                    x, row_y,
                    s=sz,
                    c=[factor_fills[s + 1]],
                    edgecolors=factor_colors[s + 1],
                    linewidths=0.6,
                    marker="o",
                    zorder=3,
                    clip_on=True,
                )

        elif ftype == "factor":
            levels = sorted(X_plot[col].astype(str).unique())
            abbrevs = _abbreviate(levels, label_chars)
            lv_map = dict(zip(levels, abbrevs))

            for xi, x in enumerate(x_pos):
                label = lv_map.get(str(X_plot[col].iloc[xi]), str(X_plot[col].iloc[xi])[:label_chars])
                ax_f.text(
                    x, row_y, label,
                    ha="center", va="center",
                    fontsize=sign_fontsize * 0.8,
                    clip_on=True,
                )

        else:
            raise ValueError(f"Unknown factor_type '{ftype}' for column '{col}'")

    # ---------------------------------------- per-row key panel
    if show_key and cell_style == "heatmap":
        ax_k = fig.add_axes([
            (left_pad + grid_w + _key_gap_r) / fw,
            bot_pad / fh,
            _key_panel_w / fw,
            grid_h / fh,
        ])
        ax_k.set_xlim(0.0, 1.0)
        ax_k.set_ylim(0.0, n_factors)
        ax_k.set_axis_off()

        # Square height in y-data units; width scaled to appear ~square in figure space
        sq_h = 0.55
        sq_w = sq_h * cell_size / _key_panel_w
        lbl_fs = 7.0  # fixed, like other axis-type text in the figure

        for fi, col in enumerate(factor_cols):
            row_y = n_factors - fi - 0.5
            ftype = ftypes[col]
            _cmap = _get_cmap(col)

            if ftype == "sign":
                present = sorted({_to_sign(v) for v in X_plot[col]})
                n_lvl = len(present)
                step = 1.0 / n_lvl
                row_norm = _make_norm(-1.0, 1.0)
                for i, lv in enumerate(present):
                    x_c = (i + 0.5) * step
                    x0 = x_c - sq_w / 2
                    color = _cmap(row_norm(float(lv)))
                    ax_k.add_patch(mpatches.Rectangle(
                        (x0, row_y - sq_h / 2), sq_w, sq_h,
                        facecolor=color, edgecolor="black", linewidth=0.3, zorder=2,
                    ))
                    ax_k.text(
                        x0 + sq_w + 0.015, row_y, str(int(lv)),
                        ha="left", va="center", fontsize=lbl_fs, clip_on=False,
                    )

            elif ftype == "continuous":
                col_max_k = global_max if normalize == "all" else max(
                    float(np.nanmax(np.abs(pd.to_numeric(X_plot[col], errors="coerce").values))),
                    1e-10,
                )
                row_norm = _make_norm(-col_max_k, col_max_k)
                lbl_lo = f"{-col_max_k:.2g}"
                lbl_hi = f"{col_max_k:.2g}"

                # Estimate text widths in x-data units (~0.055 per character)
                char_w = 0.055
                gap = 0.025
                bar_x0 = len(lbl_lo) * char_w + gap
                bar_x1 = 1.0 - len(lbl_hi) * char_w - gap
                bar_w = max(bar_x1 - bar_x0, 0.1)

                # Gradient strip: 40 thin rectangles
                N = 40
                for j in range(N):
                    t = j / (N - 1)
                    color = _cmap(row_norm(-col_max_k + 2 * col_max_k * t))
                    ax_k.add_patch(mpatches.Rectangle(
                        (bar_x0 + j * bar_w / N, row_y - sq_h / 2),
                        bar_w / N, sq_h,
                        facecolor=color, edgecolor="none", zorder=2,
                    ))
                # Outline around gradient strip
                ax_k.add_patch(mpatches.Rectangle(
                    (bar_x0, row_y - sq_h / 2), bar_w, sq_h,
                    facecolor="none", edgecolor="black", linewidth=0.3, zorder=3,
                ))
                ax_k.text(bar_x0 - gap, row_y, lbl_lo,
                          ha="right", va="center", fontsize=lbl_fs)
                ax_k.text(bar_x1 + gap, row_y, lbl_hi,
                          ha="left", va="center", fontsize=lbl_fs)

    # ---------------------------------------------------------- save / return
    if savefig is not None:
        if isinstance(savefig, str):
            savefig = [savefig]
        for fname in savefig:
            fig.savefig(fname, dpi=dpi, bbox_inches="tight")

    return fig


# ---------------------------------------------------------------------------
# Publication-ready convenience wrapper
# ---------------------------------------------------------------------------

def pub_farplot(data, response, scale=1.0, **kwargs):
    """
    farplot() with publication-ready defaults.

    Identical to :func:`farplot` but with smaller cells, a heatmap color fill
    for factor cells, clean open axes (no top/right spines on the response
    panel), a compact response panel, and grid lines on by default.

    All parameters accepted by :func:`farplot` can be passed as keyword
    arguments to override the defaults set here.

    Parameters
    ----------
    scale : float
        Uniform size multiplier applied to ``cell_size`` and
        ``response_height``. Values below 1.0 make the figure more compact;
        values above 1.0 make it larger. Default: 1.0.

    Examples
    --------
    >>> pub_farplot(df, response="y")
    >>> pub_farplot(df, response="y", scale=0.7)
    >>> pub_farplot(df, response="y", cmap="Blues", show_grid=False)
    """
    kwargs.setdefault("cell_style", "heatmap")
    kwargs.setdefault("cmap", "binary")
    kwargs.setdefault("cell_size", 0.168 * scale)
    kwargs.setdefault("response_height", 0.9 * scale)
    kwargs.setdefault("clean_axes", True)
    kwargs.setdefault("show_grid", True)
    kwargs.setdefault("show_key", True)
    kwargs.setdefault("response_color", "black")
    kwargs.setdefault("response_marker", "o")
    rc = {"font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"]}
    with plt.rc_context(rc):
        return farplot(data, response, **kwargs)
