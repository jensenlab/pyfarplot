# pyfarplot tutorial

A **farplot** (factor-and-response plot) visualizes the results of a designed
experiment. The response variable is shown as a scatter plot; directly below
it, each experimental factor is a row in a grid, and each column is one
treatment (unique factor combination). Reading down a column tells you exactly
what factor settings produced that response value.

pyfarplot is a Python port of the `farplot` function from the R
[doetools](https://github.com/jensenlab/doetools) package.

---

## Installation

```bash
pip install -e .          # from the repo root (editable install)
```

---

## Quick start

```python
import pandas as pd
from farplot import farplot, pub_farplot

df = pd.DataFrame({
    "A": [-1,  1, -1,  1, -1,  1, -1,  1],
    "B": [-1, -1,  1,  1, -1, -1,  1,  1],
    "C": [-1, -1, -1, -1,  1,  1,  1,  1],
    "y": [45, 41, 90, 67, 50, 39, 95, 66],
})

fig = farplot(df, response="y")
fig.savefig("farplot.png", dpi=150, bbox_inches="tight")
```

The `data` argument is a DataFrame whose columns are factors plus one response
column. The response column is identified by name with `response=`.

---

## Factor types

pyfarplot recognises three factor types. You can let it auto-detect them or
specify them explicitly.

| Type | Values | Rendered as |
|---|---|---|
| `"sign"` | subset of {−1, 0, +1} | **+**, **0**, or **−** characters |
| `"continuous"` | any numeric | circles sized by \|value\| and colored by sign |
| `"factor"` | strings / categories | abbreviated text labels |

Auto-detection uses `guess_factor_type()`:

```python
from farplot import guess_factor_type
guess_factor_type(df["A"])   # → 'sign'
```

Override with `factor_type`:

```python
# Single string → applies to all factors
farplot(df, response="y", factor_type="continuous")

# List → one entry per factor, in column order
farplot(df, response="y", factor_type=["sign", "continuous", "factor"])

# Dict → name each factor explicitly
farplot(df, response="y",
        factor_type={"temp": "continuous", "catalyst": "factor"})
```

---

## Symbol style (default)

The default `cell_style="symbol"` mode renders each factor cell as a text
character (+/−/0) or a sized circle.

```python
fig = farplot(
    df,
    response="y",
    cell_style="symbol",    # default
    color_signs=True,       # color +/−/0 by sign (red/gray/black)
    factor_colors=("red", "gray", "black"),
    factor_fills=("red", "white", "black"),
    normalize="all",        # scale continuous factors to a common range
    size_transform="sqrt",  # circle area ∝ |value|
)
```

### Replicate stacking

When the same treatment appears more than once, `stack_replicates=True`
(default) collapses the duplicates into a single column and shows all
individual response values stacked above it. A horizontal tick marks the mean.

```python
fig = farplot(reps, response="y", stack_replicates=True)
```

---

## Heatmap style

`cell_style="heatmap"` fills each cell with a color from a colormap instead
of drawing symbols. This is cleaner for publication figures.

```python
fig = farplot(
    df,
    response="y",
    cell_style="heatmap",
    cmap="RdBu_r",      # diverging colormap: red=low, blue=high
    show_grid=True,     # draw cell outlines
    show_key=True,      # show per-row legend to the right
    clean_axes=True,    # remove top/right spines from response panel
)
```

For sign factors the colormap is anchored so the midpoint (zero, white by
default for `"RdBu_r"`) corresponds to zero. For continuous factors the
colormap spans the observed range with the midpoint at zero.

### Colormaps

Any matplotlib colormap name works. Diverging colormaps (`"RdBu_r"`,
`"PiYG"`, `"PuOr"`) are natural for factors that span negative and positive
values. Sequential colormaps (`"Blues"`, `"viridis"`) work well when all
values have the same sign.

#### Per-factor colormaps

Pass a dict to give each factor its own colormap. The `"default"` key
covers any factor not listed explicitly:

```python
fig = pub_farplot(
    df,
    response="yield",
    factor_type="continuous",
    cmap={
        "temp":    "RdYlBu_r",
        "pressure": "PuOr",
        "default": "RdBu_r",   # 'time' uses this
    },
)
```

---

## pub_farplot — publication-ready defaults

`pub_farplot()` is a thin wrapper around `farplot()` that sets compact,
publication-ready defaults:

| Parameter | pub_farplot default | farplot default |
|---|---|---|
| `cell_style` | `"heatmap"` | `"symbol"` |
| `cmap` | `"binary"` | `"RdBu_r"` |
| `cell_size` | `0.168` in | `0.45` in |
| `response_height` | `0.9` in | `2.5` in |
| `clean_axes` | `True` | `False` |
| `show_grid` | `True` | `False` |
| `show_key` | `True` | `False` |
| `response_color` | `"black"` | `"orange"` |

The `"binary"` colormap maps −1 → white and +1 → black, which is ideal for
two-level (±1) factorial designs.

```python
fig = pub_farplot(df, response="y")
```

Any `farplot()` parameter can be passed as a keyword argument to override the
default:

```python
fig = pub_farplot(df, response="y", cmap="PiYG", show_grid=False)
```

### Scale

The `scale` parameter uniformly adjusts `cell_size` and `response_height` so
you can grow or shrink the whole figure:

```python
fig = pub_farplot(df, response="y", scale=0.7)   # more compact
fig = pub_farplot(df, response="y", scale=1.5)   # larger
```

---

## The key (legend)

When `show_key=True` and `cell_style="heatmap"`, a legend panel is drawn to
the right of the factor grid. Each row of the legend matches the corresponding
factor row.

- **Sign factors**: one colored square per level, with the level value beside
  it (e.g. `□ -1  ■ 1`).
- **Continuous factors**: a gradient strip with the minimum value on the left
  and the maximum value on the right (e.g. `-1 [▓░░▒▒▓] 1`).

---

## Response ordering and statistics

By default, treatments are sorted left-to-right by the response statistic
(`order_response=True`, `stat="mean"`). Turn this off to preserve the
original row order of the DataFrame:

```python
fig = farplot(df, response="y", order_response=False)
```

Available statistics: `"mean"` (default), `"median"`, `"min"`, `"max"`, or
any callable that takes an array and returns a scalar.

---

## Saving figures

`savefig` accepts a filename or a list of filenames. The format is inferred
from the extension. SVG and PDF are vector formats recommended for
publication; PNG is raster.

```python
# Single file
fig = farplot(df, response="y", savefig="result.svg")

# Multiple formats at once
fig = farplot(df, response="y",
              savefig=["result.svg", "result.pdf", "result.png"], dpi=300)

# Or use the returned Figure object
fig = farplot(df, response="y")
fig.savefig("result.svg", bbox_inches="tight")
```

---

## Full parameter reference

### `farplot()`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `data` | DataFrame | — | Input data |
| `response` | str | — | Name of the response column |
| `factors` | list | all non-response | Columns to use as factors |
| `factor_type` | str / list / dict | auto | `"sign"`, `"continuous"`, or `"factor"` |
| `cell_style` | str | `"symbol"` | `"symbol"` or `"heatmap"` |
| `cmap` | str / Colormap / dict | `"RdBu_r"` | Colormap(s) for heatmap style |
| `show_key` | bool | `False` | Show per-row legend in heatmap style |
| `color_signs` | bool | `True` | Color ±/0 text by sign in symbol style |
| `factor_colors` | tuple | `("red","gray","black")` | Text colors for (−, 0, +) in symbol style |
| `factor_fills` | tuple | `("red","white","black")` | Fill colors for continuous symbols |
| `normalize` | str | `"all"` | `"all"` or `"row"` — continuous factor scaling |
| `size_transform` | str / callable | `"sqrt"` | Size mapping for continuous symbols |
| `factor_size` | float | auto | Max circle area (pt²) for continuous symbols |
| `zero_size` | float | `0.1` | Relative size of zero-value continuous markers |
| `label_chars` | int | `2` | Characters for categorical label abbreviation |
| `order_response` | bool | `True` | Sort treatments by response |
| `stack_replicates` | bool | `True` | Collapse duplicate treatments |
| `stat` | str / callable | `"mean"` | Summary statistic for ordering and tick |
| `show_stat` | bool | auto | Show mean tick when stacking replicates |
| `response_color` | str | `"orange"` | Response scatter color |
| `response_marker` | str | `"o"` | Response scatter marker |
| `stat_color` | str | `"black"` | Replicate-statistic tick color |
| `cell_size` | float | `0.45` | Cell size in inches |
| `response_height` | float | `2.5` | Response panel height in inches |
| `show_grid` | bool | `False` | Draw cell outlines |
| `clean_axes` | bool | `False` | Remove top/right spines from response panel |
| `figsize` | tuple | auto | `(width, height)` in inches |
| `savefig` | str / list | `None` | Output filename(s) |
| `dpi` | int | `150` | DPI for raster output |

### `pub_farplot()`

Accepts all `farplot()` parameters plus:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `scale` | float | `1.0` | Uniform size multiplier for cells and response panel |
