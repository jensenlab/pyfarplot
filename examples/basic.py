"""
Basic farplot examples matching the doetools R tutorial.

Run from any directory:  python examples/basic.py
Outputs are written next to this script.
"""
import numpy as np
import pandas as pd
import sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from farplot import farplot

def out(name):
    return os.path.join(HERE, name)

# -----------------------------------------------------------------------
# Example 1: 2-level full factorial (sign factors)
# "chem" dataset from daewr – 4 factors, 16 runs
# -----------------------------------------------------------------------
chem = pd.DataFrame({
    "A": [-1,  1, -1,  1, -1,  1, -1,  1, -1,  1, -1,  1, -1,  1, -1,  1],
    "B": [-1, -1,  1,  1, -1, -1,  1,  1, -1, -1,  1,  1, -1, -1,  1,  1],
    "C": [-1, -1, -1, -1,  1,  1,  1,  1, -1, -1, -1, -1,  1,  1,  1,  1],
    "D": [-1, -1, -1, -1, -1, -1, -1, -1,  1,  1,  1,  1,  1,  1,  1,  1],
    "y": [45, 41, 90, 67, 50, 39, 95, 66, 47, 43, 95, 69, 40, 51, 87, 72],
})

fig1 = farplot(chem, response="y")
fig1.savefig(out("example1_chem_sign.svg"), bbox_inches="tight")
fig1.savefig(out("example1_chem_sign.png"), dpi=150, bbox_inches="tight")
print("Saved example1_chem_sign.svg / .png")

# -----------------------------------------------------------------------
# Example 2: Mixed factor types
# -----------------------------------------------------------------------
chem_mixed = chem.copy()
fig2 = farplot(
    chem_mixed,
    response="y",
    factor_type=["sign", "continuous", "sign", "factor"],
)
fig2.savefig(out("example2_mixed_types.svg"), bbox_inches="tight")
print("Saved example2_mixed_types.svg")

# -----------------------------------------------------------------------
# Example 3: Replicated design
# "eptaxr"-style dataset – 8 unique treatments, 4 replicates each
# -----------------------------------------------------------------------
rng = np.random.default_rng(42)
base = pd.DataFrame({
    "A": [-1,  1, -1,  1, -1,  1, -1,  1],
    "B": [-1, -1,  1,  1, -1, -1,  1,  1],
    "C": [-1, -1, -1, -1,  1,  1,  1,  1],
})
base = pd.concat([base] * 4, ignore_index=True)
base["y"] = 14.5 + base["A"] * (-0.3) + base["B"] * 0.4 + rng.normal(0, 0.15, len(base))

fig3 = farplot(base, response="y", stack_replicates=True)
fig3.savefig(out("example3_replicates.svg"), bbox_inches="tight")
print("Saved example3_replicates.svg")

# -----------------------------------------------------------------------
# Example 4: Continuous factors – coded on [-1, +1] so size and color both
# encode information (large red = large negative, large black = large positive)
# -----------------------------------------------------------------------
cont = pd.DataFrame({
    "temp":    [-1.0, -0.5, 0.0,  0.5,  1.0, -1.0, -0.5,  1.0],
    "pressure":[ 1.0,  1.0, 0.0, -1.0, -1.0,  0.0,  0.5, -0.5],
    "time":    [-0.5,  1.0, 0.5, -1.0,  0.5, -0.5,  1.0,  0.0],
    "yield":   [  62,   71,  68,   74,   77,   80,   75,   82],
})

fig4 = farplot(
    cont,
    response="yield",
    factor_type=["continuous", "continuous", "continuous"],
    normalize="all",
)
fig4.savefig(out("example4_continuous.svg"), bbox_inches="tight")
print("Saved example4_continuous.svg")

# -----------------------------------------------------------------------
# Example 5: Categorical factor levels
# -----------------------------------------------------------------------
cat_data = pd.DataFrame({
    "catalyst": ["Pd", "Pt", "Ni", "Pd", "Pt", "Ni"],
    "solvent":  ["MeOH", "EtOH", "MeOH", "EtOH", "MeOH", "EtOH"],
    "temp":     [-1, -1, -1, 1, 1, 1],
    "conv":     [45, 62, 38, 71, 80, 55],
})

fig5 = farplot(cat_data, response="conv")
fig5.savefig(out("example5_categorical.svg"), bbox_inches="tight")
print("Saved example5_categorical.svg")

print("\nAll examples complete.")
