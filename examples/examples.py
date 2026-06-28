"""
pyfarplot examples — run from any directory: python examples/examples.py
All output files are written next to this script.
"""
import os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from farplot import farplot, pub_farplot

def out(name):
    return os.path.join(HERE, name)


# ---------------------------------------------------------------------------
# Shared datasets
# ---------------------------------------------------------------------------

# 2-level full factorial, 4 factors, 16 runs (classic DOE)
chem = pd.DataFrame({
    "A": [-1,  1, -1,  1, -1,  1, -1,  1, -1,  1, -1,  1, -1,  1, -1,  1],
    "B": [-1, -1,  1,  1, -1, -1,  1,  1, -1, -1,  1,  1, -1, -1,  1,  1],
    "C": [-1, -1, -1, -1,  1,  1,  1,  1, -1, -1, -1, -1,  1,  1,  1,  1],
    "D": [-1, -1, -1, -1, -1, -1, -1, -1,  1,  1,  1,  1,  1,  1,  1,  1],
    "y": [45, 41, 90, 67, 50, 39, 95, 66, 47, 43, 95, 69, 40, 51, 87, 72],
})

# Continuous factors coded on [-1, +1]
cont = pd.DataFrame({
    "temp":     [-1.0, -0.5,  0.0,  0.5,  1.0, -1.0, -0.5,  1.0],
    "pressure": [ 1.0,  1.0,  0.0, -1.0, -1.0,  0.0,  0.5, -0.5],
    "time":     [-0.5,  1.0,  0.5, -1.0,  0.5, -0.5,  1.0,  0.0],
    "yield":    [  62,   71,   68,   74,   77,   80,   75,   82],
})

# Replicated design (4 replicates of 8 treatments)
rng = np.random.default_rng(42)
_base = pd.DataFrame({
    "A": [-1,  1, -1,  1, -1,  1, -1,  1],
    "B": [-1, -1,  1,  1, -1, -1,  1,  1],
    "C": [-1, -1, -1, -1,  1,  1,  1,  1],
})
reps = pd.concat([_base] * 4, ignore_index=True)
reps["y"] = 14.5 + reps["A"] * (-0.3) + reps["B"] * 0.4 + rng.normal(0, 0.15, len(reps))

# Mixed types: 2-level sign + continuous + categorical
mixed = pd.DataFrame({
    "catalyst": ["Pd", "Pt", "Ni", "Pd", "Pt", "Ni", "Pd", "Pt"],
    "temp":     [-1,   -1,   -1,    1,    1,    1,   -1,    1],
    "time":     [-0.5,  0.0,  0.5, -0.5,  0.0,  0.5, -1.0,  1.0],
    "conv":     [45,   62,   38,   71,   80,   55,   51,   76],
})


# ---------------------------------------------------------------------------
# 1. Classic symbol-style farplot (sign factors)
# ---------------------------------------------------------------------------
fig1 = farplot(chem, response="y")
fig1.savefig(out("ex1_symbol_sign.svg"), bbox_inches="tight")
fig1.savefig(out("ex1_symbol_sign.png"), dpi=150, bbox_inches="tight")
print("ex1  symbol / sign factors")


# ---------------------------------------------------------------------------
# 2. Symbol style with replicate stacking
# ---------------------------------------------------------------------------
fig2 = farplot(reps, response="y", stack_replicates=True)
fig2.savefig(out("ex2_symbol_replicates.svg"), bbox_inches="tight")
print("ex2  symbol / replicate stacking")


# ---------------------------------------------------------------------------
# 3. Symbol style with continuous factors
#    (circle size encodes |value|; color encodes sign)
# ---------------------------------------------------------------------------
fig3 = farplot(
    cont,
    response="yield",
    factor_type="continuous",
    normalize="all",
)
fig3.savefig(out("ex3_symbol_continuous.svg"), bbox_inches="tight")
print("ex3  symbol / continuous factors")


# ---------------------------------------------------------------------------
# 4. Symbol style with mixed factor types (sign + continuous + categorical)
# ---------------------------------------------------------------------------
fig4 = farplot(
    mixed,
    response="conv",
    factor_type={"catalyst": "factor", "temp": "sign", "time": "continuous"},
)
fig4.savefig(out("ex4_symbol_mixed.svg"), bbox_inches="tight")
print("ex4  symbol / mixed factor types")


# ---------------------------------------------------------------------------
# 5. Heatmap style (cell_style='heatmap') with default RdBu_r colormap
# ---------------------------------------------------------------------------
fig5 = farplot(
    chem,
    response="y",
    cell_style="heatmap",
    show_key=True,
    show_grid=True,
    clean_axes=True,
    response_color="black",
)
fig5.savefig(out("ex5_heatmap_default.svg"), bbox_inches="tight")
print("ex5  heatmap / default cmap")


# ---------------------------------------------------------------------------
# 6. pub_farplot — publication-ready defaults
#    binary cmap, compact cells, clean axes, key legend
# ---------------------------------------------------------------------------
fig6 = pub_farplot(chem, response="y")
fig6.savefig(out("ex6_pub_sign.svg"), bbox_inches="tight")
fig6.savefig(out("ex6_pub_sign.png"), dpi=150, bbox_inches="tight")
print("ex6  pub_farplot / sign factors")


# ---------------------------------------------------------------------------
# 7. pub_farplot with continuous factors
# ---------------------------------------------------------------------------
fig7 = pub_farplot(
    cont,
    response="yield",
    factor_type="continuous",
    cmap="RdBu_r",
)
fig7.savefig(out("ex7_pub_continuous.svg"), bbox_inches="tight")
print("ex7  pub_farplot / continuous factors")


# ---------------------------------------------------------------------------
# 8. pub_farplot with per-factor colormaps
#    Each factor gets its own colormap; 'default' covers anything not listed.
# ---------------------------------------------------------------------------
fig8 = pub_farplot(
    cont,
    response="yield",
    factor_type="continuous",
    cmap={
        "temp":     "RdYlBu_r",
        "pressure": "PuOr",
        "default":  "RdBu_r",    # 'time' falls back to this
    },
)
fig8.savefig(out("ex8_pub_per_factor_cmap.svg"), bbox_inches="tight")
fig8.savefig(out("ex8_pub_per_factor_cmap.png"), dpi=150, bbox_inches="tight")
print("ex8  pub_farplot / per-factor colormaps")


# ---------------------------------------------------------------------------
# 9. pub_farplot with mixed types and per-factor cmaps
# ---------------------------------------------------------------------------
fig9 = pub_farplot(
    mixed,
    response="conv",
    factor_type={"catalyst": "factor", "temp": "sign", "time": "continuous"},
    cmap={"time": "viridis", "default": "binary"},
)
fig9.savefig(out("ex9_pub_mixed.svg"), bbox_inches="tight")
fig9.savefig(out("ex9_pub_mixed.png"), dpi=150, bbox_inches="tight")
print("ex9  pub_farplot / mixed types + per-factor cmaps")


# ---------------------------------------------------------------------------
# 10. pub_farplot scale parameter
# ---------------------------------------------------------------------------
for s in (0.7, 1.0, 1.5):
    fig = pub_farplot(chem, response="y", scale=s)
    fig.savefig(out(f"ex10_pub_scale{s:.1f}.png"), dpi=150, bbox_inches="tight")
print("ex10 pub_farplot / scale 0.7 / 1.0 / 1.5")


# ---------------------------------------------------------------------------
# 11. Saving to multiple formats at once
# ---------------------------------------------------------------------------
pub_farplot(
    chem,
    response="y",
    savefig=[out("ex11_multiformat.svg"), out("ex11_multiformat.pdf"), out("ex11_multiformat.png")],
    dpi=300,
)
print("ex11 multi-format export (.svg / .pdf / .png)")


print("\nAll examples written to", HERE)
