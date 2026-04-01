"""Hydrogen atom orbitals — computation and 3D/2D visualisation.

Physics
-------
ψ_{nlm}(r, θ, φ) = R_{nl}(r) · Y_l^m(θ, φ)

Radial part:
  R_{nl}(r) = N_{nl} · e^{-ρ/2} · ρ^l · L_{n-l-1}^{2l+1}(ρ)
  ρ = 2r / (n·a₀)
  N_{nl} = sqrt( (2/(n·a₀))³ · (n-l-1)! / (2n·(n+l)!) )

Angular part: scipy.special.sph_harm_y (scipy ≥ 1.13) or sph_harm (older)
"""

from math import factorial

import matplotlib.pyplot as plt
import numpy as np
from scipy.special import genlaguerre
try:
    # scipy ≥ 1.13: sph_harm_y(l, m, theta_polar, phi_azim)
    from scipy.special import sph_harm_y as _sph_harm_y
    def _sph_harm(m, l, phi, theta):
        return _sph_harm_y(l, m, theta, phi)
except ImportError:
    # older scipy: sph_harm(m, l, phi_azim, theta_polar)
    from scipy.special import sph_harm as _sph_harm_legacy
    def _sph_harm(m, l, phi, theta):
        return _sph_harm_legacy(m, l, phi, theta)

from config import A0, LABEL_FONTSIZE, TITLE_FONTSIZE

_ORBITAL_NAMES = {0: "s", 1: "p", 2: "d", 3: "f", 4: "g", 5: "h"}


# ── Pure physics ──────────────────────────────────────────────────────────────

def _radial(n, l, r):
    """Return the normalised radial wave function R_{nl}(r) evaluated at r."""
    rho = 2.0 * r / (n * A0)
    norm = np.sqrt(
        (2.0 / (n * A0)) ** 3
        * factorial(n - l - 1)
        / (2 * n * factorial(n + l))
    )
    L = genlaguerre(n - l - 1, 2 * l + 1)
    rho_l = 1.0 if l == 0 else rho ** l
    return norm * np.exp(-rho / 2.0) * rho_l * L(rho)


def compute(n, l, m, resolution=45):
    """Compute |ψ_{nlm}|² on a cubic Cartesian grid.

    Parameters
    ----------
    n, l, m    : quantum numbers  (1 ≤ n ≤ 4,  0 ≤ l < n,  |m| ≤ l)
    resolution : number of grid points per axis

    Returns
    -------
    dict with keys:
        X, Y, Z      — coordinate arrays in metres, shape (res, res, res)
        psi2         — probability density normalised to peak = 1
        psi2_raw_peak — raw peak before normalisation (SI units of 1/m³)
        r_max        — grid half-extent in metres
        n, l, m      — quantum numbers
    """
    r_max = A0 * n * n * 5.0
    coords = np.linspace(-r_max, r_max, resolution)
    X, Y, Z = np.meshgrid(coords, coords, coords, indexing="ij")

    r = np.sqrt(X**2 + Y**2 + Z**2)
    r_safe = np.where(r < 1e-15, 1e-15, r)

    theta = np.arccos(np.clip(Z / r_safe, -1.0, 1.0))  # polar   [0, π]
    phi   = np.arctan2(Y, X)                             # azimuth [−π, π]

    R_nl = _radial(n, l, r_safe)
    Y_lm = _sph_harm(m, l, phi, theta)

    psi2 = np.abs(R_nl * Y_lm) ** 2
    peak = psi2.max()
    if peak > 0:
        psi2 = psi2 / peak

    return dict(X=X, Y=Y, Z=Z, psi2=psi2, psi2_raw_peak=peak,
                r_max=r_max, n=n, l=l, m=m)


# ── Visualisation ─────────────────────────────────────────────────────────────

def _psi2_on_plane(n, l, m, r_max_m, res, fixed_axis, fixed_val_m, global_peak):
    """Analytically evaluate |ψ_{nlm}|² on a full square plane.

    Parameters
    ----------
    fixed_axis  : 'z' → XY plane (horizontal),  'y' → XZ plane (vertical)
    fixed_val_m : position of the plane in metres
    global_peak : raw peak of |ψ|² from compute() — normalises consistently
                  so planes far from the orbital show genuinely near-zero density.

    Returns X, Y, Z (shape res×res, in Ångström) and P (normalised [0,1]).
    """
    coords = np.linspace(-r_max_m, r_max_m, res)
    A, B   = np.meshgrid(coords, coords, indexing="ij")
    C      = np.full_like(A, fixed_val_m)

    if fixed_axis == "z":
        Xm, Ym, Zm = A, B, C
    else:                           # 'y' → XZ plane
        Xm, Ym, Zm = A, C, B

    r_safe = np.where((Xm**2 + Ym**2 + Zm**2) < 1e-30,
                      1e-15,
                      np.sqrt(Xm**2 + Ym**2 + Zm**2))
    theta = np.arccos(np.clip(Zm / r_safe, -1.0, 1.0))
    phi   = np.arctan2(Ym, Xm)

    P = np.abs(_radial(n, l, r_safe) * _sph_harm(m, l, phi, theta)) ** 2
    if global_peak > 0:
        P = P / global_peak   # global normalisation: same scale as 3D psi2

    return Xm * 1e10, Ym * 1e10, Zm * 1e10, P


def plot_orbital_3d(data, iso_level=0.15, cross_res=150,
                    fixed_axis="z", plane_pos_A=0.0):
    """Interactive Plotly 3D figure: ghost isosurface + draggable cutting plane.

    The full isosurface is rendered at very low opacity (ghost/outline) so
    the cutting plane density map is always clearly visible through it.
    Rotate with mouse-drag, zoom with scroll wheel.

    Parameters
    ----------
    fixed_axis  : 'z' for horizontal XY plane, 'y' for vertical XZ plane
    plane_pos_A : plane position in Ångström
    cross_res   : number of grid points per axis on the cutting plane
    """
    import plotly.graph_objects as go
    from skimage.measure import marching_cubes
    from scipy.ndimage import zoom as nd_zoom

    n, l, m  = data["n"], data["l"], data["m"]
    psi2     = data["psi2"]
    r_max_A  = data["r_max"] * 1e10
    r_max_m  = data["r_max"]
    N        = psi2.shape[0]
    raw_peak = data["psi2_raw_peak"]

    # ── Ghost isosurface (full mesh, very low opacity) ─────────────────────
    target  = 120
    zoom_f  = target / N
    psi2_mc = np.clip(nd_zoom(psi2, zoom_f, order=3), 0.0, 1.0) if zoom_f > 1.05 else psi2
    N_mc    = psi2_mc.shape[0]
    level   = float(min(iso_level, psi2.max() * 0.95))
    spacing = (2.0 * r_max_A / (N_mc - 1),) * 3

    traces = []
    try:
        verts, faces, _, _ = marching_cubes(psi2_mc, level=level, spacing=spacing)
        verts -= r_max_A
        traces.append(go.Mesh3d(
            x=verts[:, 0], y=verts[:, 1], z=verts[:, 2],
            i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
            color="steelblue",
            opacity=0.20,                    # ghost — visible but doesn't obscure plane
            showscale=False,
            hoverinfo="skip",
            name="Isovlak",
        ))
    except (ValueError, RuntimeError):
        pass

    # ── Analytical cutting plane ───────────────────────────────────────────
    plane_pos_m = plane_pos_A * 1e-10
    Xp, Yp, Zp, P = _psi2_on_plane(n, l, m, r_max_m, cross_res,
                                    fixed_axis, plane_pos_m, raw_peak)
    # Show full colormap: zero density → black (low end of "hot"), no transparency

    traces.append(go.Surface(
        x=Xp, y=Yp, z=Zp,
        surfacecolor=P,
        colorscale="Hot",
        cmin=0, cmax=1,
        showscale=True,
        colorbar=dict(title="|ψ|²", len=0.5, x=0.92),
        opacity=1.0,
        hoverinfo="skip",
        name="Snijvlak",
    ))

    # ── Layout ─────────────────────────────────────────────────────────────
    name     = f"{n}{_ORBITAL_NAMES.get(l, str(l))}"
    ax_label = "z" if fixed_axis == "z" else "y"
    plane_lbl = f"XY  (z = {plane_pos_A:.1f} Å)" if fixed_axis == "z" \
                else f"XZ  (y = {plane_pos_A:.1f} Å)"

    fig = go.Figure(data=traces)
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="x (Å)", range=[-r_max_A, r_max_A]),
            yaxis=dict(title="y (Å)", range=[-r_max_A, r_max_A]),
            zaxis=dict(title="z (Å)", range=[-r_max_A, r_max_A]),
            aspectmode="cube",
            camera=dict(eye=dict(x=1.6, y=1.6, z=1.0)),
        ),
        title=dict(
            text=(f"Orbitaal {name}  (n={n}, l={l}, m={m})  —  "
                  f"isovlak |ψ|²={level:.2f}  |  snijvlak {plane_lbl}"),
            font=dict(size=TITLE_FONTSIZE),
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        height=650,
    )
    return fig


def plot_orbital_2d(data, res=150):
    """Side-by-side 2D cross-sections: xz-plane (y=0) and xy-plane (z=0)."""
    r_max_A = data["r_max"] * 1e10
    n, l, m = data["n"], data["l"], data["m"]
    global_peak = data["psi2_raw_peak"]
    r_max_m = data["r_max"]

    extent = [-r_max_A, r_max_A, -r_max_A, r_max_A]
    name   = f"{n}{_ORBITAL_NAMES.get(l, str(l))}"

    # Evaluate analytically at the requested resolution
    _, _, _, psi_xz = _psi2_on_plane(n, l, m, r_max_m, res, "y", 0.0, global_peak)
    _, _, _, psi_xy = _psi2_on_plane(n, l, m, r_max_m, res, "z", 0.0, global_peak)
    psi_xz = psi_xz.T   # (res, res) with z on vertical axis
    psi_xy = psi_xy.T   # (res, res) with y on vertical axis

    coords = np.linspace(-r_max_A, r_max_A, res)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    # xz-plane (y = 0) ── z on vertical axis
    im1 = ax1.imshow(
        psi_xz, origin="lower", extent=extent,
        cmap="hot", aspect="equal", vmin=0, vmax=1,
    )
    ax1.contour(
        coords, coords,
        psi_xz, levels=7, colors="white", alpha=0.35, linewidths=0.6,
    )
    ax1.set_title(f"xz-vlak  (y=0)  —  {name}", fontsize=TITLE_FONTSIZE - 1)
    ax1.set_xlabel("x ($\AA$)", fontsize=LABEL_FONTSIZE)
    ax1.set_ylabel("z ($\AA$)", fontsize=LABEL_FONTSIZE)
    fig.colorbar(im1, ax=ax1, label=r"$|\psi|^2$")

    # xy-plane (z = 0) ── y on vertical axis
    im2 = ax2.imshow(
        psi_xy, origin="lower", extent=extent,
        cmap="hot", aspect="equal", vmin=0, vmax=1,
    )
    ax2.contour(
        coords, coords,
        psi_xy, levels=7, colors="white", alpha=0.35, linewidths=0.6,
    )
    ax2.set_title(f"xy-vlak  (z=0)  —  {name}", fontsize=TITLE_FONTSIZE - 1)
    ax2.set_xlabel("x ($\AA$)", fontsize=LABEL_FONTSIZE)
    ax2.set_ylabel("y ($\AA$)", fontsize=LABEL_FONTSIZE)
    fig.colorbar(im2, ax=ax2, label=r"$|\psi|^2$")

    try:
        fig.tight_layout()
    except Exception:
        pass

    return fig
