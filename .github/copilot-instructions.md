# Copilot Instructions for QuantMini

This is a Streamlit + matplotlib physics education app demonstrating quantum mechanics experiments.

## Architecture
- `physics/` — pure computation and plotting; no Streamlit imports allowed here
  - `compute()` returns a plain dict of arrays and scalars
  - `plot_*()` accepts that dict and returns a `matplotlib.figure.Figure`
- `views/` — Streamlit UI only; calls `physics/` functions, renders results
- `config.py` — single source of truth for all physical constants and figure sizes; never hardcode constants elsewhere
- `app.py` — navigation only; one `render()` call per experiment

## Conventions
- Physical constants (`H`, `KB`, `C`, `E`, `SIGMA`) live in `config.py` and must be imported from there
- Figure sizes come from `config.py` (`FIGSIZE`, `FIGSIZE_SCHEMA`, etc.)
- Always wrap `fig.tight_layout()` in try/except to avoid remote rendering crashes
- Avoid mathtext strings like `$S_1$` in labels unless known to work on the target matplotlib version; prefer plain text
- Measurement noise uses Poisson statistics: `sigma = sqrt(I * I_peak / N_peak)`
- Rainbow visible-light bands use `LinearSegmentedColormap` with violet→red matching the x-axis direction

## Style
- Dutch labels in the UI (sliders, tabs, metric cards, axis labels)
- Seaborn "deep" palette for multi-line plots
- Fixed x-axis ranges where physically meaningful (e.g. ±20 mm for double slit)
- Always show both the "wave" and "particle" patterns in the double slit intensity plot
- Theory tabs use `st.latex()` for equations and two-column layout

## Adding a new experiment
1. Create `physics/<name>.py` with `compute()` and `plot_*()` functions
2. Create `views/<name>.py` with a `render()` function using Streamlit sidebar for controls
3. Register it in `app.py` navigation
4. Update `README.md` to document the new experiment, its controls, and any new physical concepts shown

## Maintaining README.md
- Update `README.md` whenever a new experiment is added, a significant feature changes, or new sliders/toggles are introduced
- Keep the experiment descriptions in sync with the actual UI labels (Dutch) 
