"""Shared physical constants, material data, and plot style."""

H     = 6.626e-34   # Planck constant (J s)
E     = 1.602e-19   # Elementary charge (C)
C     = 2.998e8     # Speed of light (m/s)
KB    = 1.381e-23   # Boltzmann constant (J/K)
SIGMA = 5.670e-8    # Stefan-Boltzmann constant (W/(m² K⁴))
A0    = 5.292e-11   # Bohr radius (m)

# Wien displacement constant: b = h·c / (k_B · x0)
# where x0 ≈ 4.9651 solves  x·eˣ/(eˣ−1) = 5
_WIEN_X0 = 4.965114231744276
WIEN_B   = H * C / (KB * _WIEN_X0)   # ≈ 2.898e-3 m·K

# Shared plot style
FIGSIZE_WIDE   = (10, 5)   # standard data plots
FIGSIZE_SCHEMA = (2.5, 1.8)  # schematic diagram
LABEL_FONTSIZE  = 12
TITLE_FONTSIZE  = 13
LEGEND_FONTSIZE = 10
GRID_ALPHA      = 0.3

METALS = {
    "Cesium":    1.95,
    "Kalium":    2.29,
    "Natrium":   2.30,
    "Aluminium": 4.06,
    "Koper":     4.70,
}

METAL_COLORS = {
    "Cesium":    "#4C72B0",
    "Kalium":    "#55A868",
    "Natrium":   "#DD8452",
    "Aluminium": "#C44E52",
    "Koper":     "#8172B3",
}
