"""Shared physical constants, material data, and plot style."""

H = 6.626e-34   # Planck constant (J s)
E = 1.602e-19   # Elementary charge (C)
C = 2.998e8     # Speed of light (m/s)

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
