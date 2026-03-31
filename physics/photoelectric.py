"""Computation and plotting for the photoelectric effect."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import linregress

from config import H, E, C, METALS, METAL_COLORS, FIGSIZE_WIDE, LABEL_FONTSIZE, TITLE_FONTSIZE, LEGEND_FONTSIZE, GRID_ALPHA


def compute(W_eV, noise_level):
    """Compute all physics data for the photoelectric effect."""
    W = W_eV * E
    nu_c = W / H

    np.random.seed(4)
    nu_meas = np.linspace(nu_c * 1.04, nu_c * 1.44, 8)
    V_ideal = (H * nu_meas - W) / E
    V_meas = V_ideal + np.random.normal(0, noise_level, size=len(nu_meas))

    slope, intercept, *_ = linregress(nu_meas, V_meas)
    nu_c_fit = -intercept / slope

    nu_full = np.linspace(0, nu_c * 1.52, 500)
    V_theory = (H * nu_full - W) / E
    V_physical = np.maximum(V_theory, 0)

    nu_fit = np.linspace(nu_c_fit, max(nu_meas) * 1.02, 200)
    V_fit = slope * nu_fit + intercept

    return dict(
        W=W, nu_c=nu_c, nu_meas=nu_meas, V_meas=V_meas,
        slope=slope, intercept=intercept, nu_c_fit=nu_c_fit,
        nu_full=nu_full, V_theory=V_theory, V_physical=V_physical,
        nu_fit=nu_fit, V_fit=V_fit,
    )


def plot_main(data, title, show_extrap, show_fit):
    """Create the main V_stop vs frequency figure."""
    d = data
    y_max = max(d["V_meas"].max(), d["V_physical"].max()) * 1.25

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)

    # Shaded regions
    ax.axvspan(0, d["nu_c"], alpha=0.13, color="gray")
    ax.axvspan(d["nu_c"], max(d["nu_full"]), alpha=0.10, color="green")

    if show_extrap:
        ax.plot(d["nu_full"], d["V_theory"], color="gray", ls=":", lw=2,
                label=r"$h\nu - W$ (extrapolatie)")

    ax.plot(d["nu_full"], d["V_physical"], color="royalblue", lw=4,
            label=r"Theoretische $V_\mathrm{stop}$")
    ax.scatter(d["nu_meas"], d["V_meas"], color="black", s=80, zorder=5,
               label="Meetpunten")

    if show_fit:
        ax.plot(d["nu_fit"], d["V_fit"], color="firebrick", lw=2.5, ls="--",
                label="Lineaire fit")

    ax.scatter([d["nu_c"]], [0], color="firebrick", s=160, marker="D",
               zorder=6, label=r"$\nu_c$ (theorie)")
    ax.axvline(x=d["nu_c"], color="firebrick", ls="--", lw=1.5, alpha=0.7)
    ax.axhline(y=0, color="black", lw=1)

    ax.annotate(
        rf'$\nu_c \approx {d["nu_c"]:.2e}$ Hz',
        xy=(d["nu_c"], 0),
        xytext=(d["nu_c"] - 0.28e14, 0.28),
        arrowprops=dict(arrowstyle="->", color="black", lw=1.3),
        fontsize=11,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9),
    )

    ax.text(d["nu_c"] * 0.44, 0.20 * y_max,
            r"Voor $\nu < \nu_c$:" + "\n" + r"$h\nu < W$, geen emissie",
            fontsize=10, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85))
    ax.text(d["nu_c"] * 1.25, 0.67 * y_max,
            r"Voor $\nu > \nu_c$:" + "\n"
            + r"$V_\mathrm{stop} = \dfrac{h\nu - W}{e}$",
            fontsize=11, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85))
    ax.text(d["nu_c"] * 0.44, y_max * 0.91, "Geen emissie",
            ha="center", fontsize=10, color="dimgray", style="italic")
    ax.text(d["nu_c"] * 1.25, y_max * 0.91, "Wel emissie",
            ha="center", fontsize=10, color="darkgreen", style="italic")

    ax.set_xlim(0, max(d["nu_full"]))
    ax.set_ylim(-0.15, y_max)
    ax.set_xlabel(r"$\nu$ (Hz)", fontsize=LABEL_FONTSIZE)
    ax.set_ylabel(r"$V_\mathrm{stop}$ (V)", fontsize=LABEL_FONTSIZE)
    ax.set_title(title, fontsize=TITLE_FONTSIZE, fontweight="bold")
    ax.legend(loc="upper left", fontsize=LEGEND_FONTSIZE)
    ax.grid(True, alpha=GRID_ALPHA)
    plt.tight_layout()
    return fig


def plot_metals():
    """Create the metals comparison figure."""
    nu_range = np.linspace(0, 13e14, 500)

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    ax.axhline(y=0, color="black", lw=1)

    # Rainbow visible-light band (380–700 nm → 4.28e14–7.89e14 Hz)
    rainbow_colors = [
        (0.45, 0.0,  0.75),  # violet
        (0.0,  0.0,  1.0),   # blue
        (0.0,  0.8,  0.8),   # cyan
        (0.0,  0.8,  0.0),   # green
        (1.0,  1.0,  0.0),   # yellow
        (1.0,  0.5,  0.0),   # orange
        (1.0,  0.0,  0.0),   # red
    ]
    rainbow_cmap = LinearSegmentedColormap.from_list("rainbow_vis", rainbow_colors)
    nu_vis_lo, nu_vis_hi = 4.28e14, 7.89e14
    rainbow_img = np.linspace(1, 0, 256).reshape(1, -1)  # reversed: violet@high-ν, red@low-ν
    ax.imshow(
        rainbow_img, cmap=rainbow_cmap, aspect="auto", alpha=0.22,
        extent=[nu_vis_lo, nu_vis_hi, -0.1, 3.7],
        origin="lower", zorder=0,
    )

    for naam, W_eV in METALS.items():
        nu_c = W_eV * E / H
        V = np.maximum((H * nu_range - W_eV * E) / E, 0)
        label = rf"{naam} ($W={W_eV}$ eV)"
        ax.plot(nu_range, V, color=METAL_COLORS[naam], lw=2.5, label=label)
        ax.axvline(x=nu_c, color=METAL_COLORS[naam], ls=":", lw=1, alpha=0.5)

    ax.set_xlim(0, 13e14)
    ax.set_ylim(-0.1, 3.7)
    ax.set_xlabel(r"Frequentie $\nu$ (Hz)", fontsize=LABEL_FONTSIZE)
    ax.set_ylabel(r"$V_\mathrm{stop}$ (V)", fontsize=LABEL_FONTSIZE)


    # Secondary wavelength axis at the top (lambda = c/nu, non-linear)
    def nu_to_nm(nu):
        with np.errstate(divide="ignore", invalid="ignore"):
            safe = np.where(nu > 1e10, nu, 1e10)
            return C / safe * 1e9

    def nm_to_nu(lam_nm):
        with np.errstate(divide="ignore", invalid="ignore"):
            safe = np.where(lam_nm > 1e-3, lam_nm, 1e-3)
            return C / (safe * 1e-9)

    ax2 = ax.secondary_xaxis("top", functions=(nu_to_nm, nm_to_nu))
    ax2.set_xlabel(r"Golflengte $\lambda$ (nm)", fontsize=LABEL_FONTSIZE)
    # Explicit ticks at round wavelengths (hyperbolic scale — auto ticks won't work)
    lam_ticks_nm = [230, 280, 350, 400, 500, 600, 750, 1000, 1500, 3000]
    nu_for_ticks = [C / (l * 1e-9) for l in lam_ticks_nm]
    # Only show ticks within the primary x-axis range
    xlim = ax.get_xlim()
    visible = [(nu, lam) for nu, lam in zip(nu_for_ticks, lam_ticks_nm)
               if xlim[0] <= nu <= xlim[1]]
    if visible:
        ax2.set_xticks([nu_to_nm(nu) for nu, _ in visible])
        ax2.set_xticklabels([str(lam) for _, lam in visible])

    ax.legend(fontsize=LEGEND_FONTSIZE)
    ax.grid(True, alpha=GRID_ALPHA)
    try:
        fig.tight_layout()
    except Exception:
        pass
    return fig
