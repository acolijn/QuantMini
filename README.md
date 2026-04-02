# QuantMini — Interactieve Kwantumfysica

An interactive web application for exploring three foundational quantum physics experiments, built with [Streamlit](https://streamlit.io) and Matplotlib.

---

## Experiments

### ⚡ Foto-elektrisch effect
Simulate Einstein's photoelectric effect:
- Select the **material** (work function) via sidebar
- Toggle **linear fit** and **extrapolation** lines on/off
- Adjustable **measurement noise**
- Metric cards: afkapfrequentie (theorie), afkapfrequentie (fit), h uit fit, h (literatuur)
- **Vergelijking tab**: all metals side-by-side with a rainbow visible-light band, secondary wavelength axis (λ = c/ν)
- **Theory tab**: Einstein equation, stopping voltage, cutoff frequency, constants table

### 🌊 Dubbele-spleet experiment
Explore wave–particle duality:
- Adjust slit separation **d**, slit width **a**, wavelength **λ**, screen distance **L**
- Intensity pattern shows **wave interference** (solid) and **classical particle** (dashed) simultaneously
- Δy fringe-spacing arrow annotated above the plot
- Fixed x-axis ±20 mm for direct visual comparison when parameters change
- Metric cards: fringe-afstand Δy, golflengte λ, spleetafstand d
- Schematic diagrams of both situations (with/without which-path observation)
- **Theory tab**: intensity formula, fringe spacing, de Broglie wavelength, current parameter values

### 🌡 Zwarte-lichaamsstraling
Planck vs classical physics:
- Adjust **temperature** (100 K – 10 000 K)
- **Planck spectrum** with simulated measurement points and **Poisson error bars**; toggle measurement points on/off
- **Rayleigh-Jeans** classical approximation overlaid (toggle)
- Adjustable **measurement noise** (controls effective photon count: σ ∝ √I)
- Optional **log scale** to dramatically reveal the ultraviolet catastrophe
- Rainbow visible-light band (380–700 nm), auto-switching between nm and µm axes
- Wien peak marked with a dotted line
- Metric cards: temperatuur, λ_max (Wien), kleur piek (spectral region), uitgestraald vermogen (Stefan-Boltzmann)
- **Theory tab**: Planck's law, Rayleigh-Jeans, Wien's displacement law, Stefan-Boltzmann law with σ derived from fundamental constants

### ⚛️ Waterstof-orbitalen
3-D probability densities of hydrogen atom wave functions (rendered with Plotly):
- Choose quantum numbers **n** (1–6), **l** (0 … n−1), **m** (−l … +l) via sidebar
- Tune the **display threshold** to show more or fewer probability-density voxels
- Adjust **doorsnede resolutie** (50–300) for sampling resolution of cross-sections
- **3D tab**: semi-transparent isosurface with an interactive cutting plane (XY or XZ orientation); drag the plane position slider or use the play/pause animation to sweep through the orbital; rotate by mouse-dragging the canvas
- Metric cards: orbital name (1s, 2p, …), energy level (eV), mean radius (Å), number of radial nodes
- **Doorsnedes tab**: side-by-side false-colour images of |ψ|² in the xz-plane (y = 0) and xy-plane (z = 0) with white contour lines
- **Theory tab**: wave function formula, radial part with associated Laguerre polynomials, energy levels, mean radius, radial probability density

---

## Project Structure

```
QuantMini/
├── app.py                  # Streamlit entry point, page routing, global CSS
├── config.py               # Physical constants, material data, plot style
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── physics/
│   ├── blackbody.py        # Planck, Rayleigh-Jeans, Wien, noise, plotting
│   ├── double_slit.py      # Interference, single-slit envelope, schema, plotting
│   ├── hydrogen.py         # Hydrogen wave functions, 3D cutaway & 2D cross-sections
│   └── photoelectric.py    # Einstein equation, linear fit, plotting
└── views/
    ├── blackbody.py        # Streamlit UI: sidebar sliders, tabs
    ├── double_slit.py      # Streamlit UI: sidebar sliders, tabs, schema
    ├── hydrogen.py         # Streamlit UI: quantum number selectors, 3D/2D tabs, theory
    └── photoelectric.py    # Streamlit UI: sidebar sliders, tabs, metal comparison
```

**`physics/`** — pure computation and Matplotlib figures, no Streamlit dependency.  
**`views/`** — thin Streamlit layer: sliders, toggles, layout, calling physics functions.

---

## Running Locally

### Without Docker

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

### With Docker Compose

```bash
docker compose up --build
```

Open [http://localhost:8502](http://localhost:8502).

The container runs on port **8502** (mapped to the same port on the host).

---

## Physical Constants

| Symbol | Value | Description |
|--------|-------|-------------|
| h | 6.626 × 10⁻³⁴ J·s | Planck constant |
| e | 1.602 × 10⁻¹⁹ C | Elementary charge |
| c | 2.998 × 10⁸ m/s | Speed of light |
| k_B | 1.381 × 10⁻²³ J/K | Boltzmann constant |
| σ | 5.670 × 10⁻⁸ W·m⁻²·K⁻⁴ | Stefan-Boltzmann constant |

---

## Dependencies

| Package | Version |
|---------|---------|
| streamlit | ≥ 1.55, < 2 |
| matplotlib | ≥ 3.10, < 4 |
| numpy | ≥ 2.2, < 3 |
| scipy | ≥ 1.15, < 2 |
| plotly | ≥ 5.0, < 7 |
| scikit-image | ≥ 0.22, < 2 |
