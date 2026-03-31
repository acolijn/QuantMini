"""Computation and plotting for the double-slit experiment."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.transforms import blended_transform_factory

from config import FIGSIZE_WIDE, FIGSIZE_SCHEMA, LABEL_FONTSIZE, TITLE_FONTSIZE, LEGEND_FONTSIZE, GRID_ALPHA


def compute(d, lam, L, a):
    """Compute intensities for the double-slit experiment."""
    y_max_m = 20e-3  # fixed ±20 mm
    y = np.linspace(-y_max_m, y_max_m, 2000)

    beta = np.pi * a * y / (lam * L)
    delta = np.pi * d * y / (lam * L)
    sinc = np.where(np.abs(beta) < 1e-10, 1.0, np.sin(beta) / beta)

    I_wave = (sinc * np.cos(delta)) ** 2
    I_wave /= I_wave.max()

    sigma = 0.8 * lam * L / a
    I_slit1_raw = np.exp(-0.5 * ((y - d / 2) / sigma) ** 2)
    I_slit2_raw = np.exp(-0.5 * ((y + d / 2) / sigma) ** 2)
    I_particle = I_slit1_raw + I_slit2_raw
    norm = I_particle.max()
    I_particle = I_particle / norm
    I_slit1 = I_slit1_raw / norm
    I_slit2 = I_slit2_raw / norm

    dy_fringe = lam * L / d

    return dict(
        y=y, I_wave=I_wave, I_particle=I_particle,
        I_slit1=I_slit1, I_slit2=I_slit2, dy_fringe=dy_fringe,
    )


def plot_schema(data, d, lam, L, a, waarneming):
    """Create the schematic side-view figure of the double-slit setup."""
    I_draw = data["I_particle"] if waarneming else data["I_wave"]

    fig, ax = plt.subplots(figsize=FIGSIZE_SCHEMA)
    ax.set_xlim(0, 12)
    ax.set_ylim(-9.5, 9.5)
    ax.set_aspect("equal")
    ax.axis("off")

    title = ("Met waarneming"
             if waarneming else "Zonder waarneming")
    ax.set_title(title, fontsize=7)

    # Source
    ax.add_patch(patches.Circle((0.7, 0), 0.22, color="gold",
                                ec="darkorange", lw=1.0, zorder=5))
    """ for ang in np.linspace(-0.45, 0.45, 5):
        dx, dy = np.cos(ang), np.sin(ang)
        ax.annotate("", xy=(0.7 + 1.0 * dx, dy),
                     xytext=(0.7 + 0.45 * dx, 0.45 * dy),
                     arrowprops=dict(arrowstyle="->", color="goldenrod", lw=0.8)) """
    ax.text(0.7, -1.35, "bron", ha="center", fontsize=7, color="darkorange")

    # Slit screen
    sx = 5.5
    slit_half = 1.1
    gap = 0.2
    for y0, y1 in [(-8.5, -(slit_half + gap)),
                    (-(slit_half - gap), (slit_half - gap)),
                    ((slit_half + gap), 8.5)]:
        ax.plot([sx, sx], [y0, y1], color="#333333", lw=2, solid_capstyle="butt")
    ax.text(sx - 0.55, slit_half + gap + 0.4, r"$S_1$", ha="right", fontsize=8)
    ax.text(sx - 0.55, -(slit_half + gap + 0.4), r"$S_2$", ha="right", fontsize=8)

    # Detector (if observing)


    # Rays
    scr = 10.3
    if not waarneming:
        for y_slit in [slit_half + gap, -(slit_half + gap)]:
            for frac in np.linspace(-0.55, 0.55, 9):
                y_end = y_slit + frac * 6.5
                ax.annotate("", xy=(scr - 0.15, y_end),
                            xytext=(sx + 0.15, y_slit),
                            arrowprops=dict(arrowstyle="->", color="steelblue",
                                            lw=0.5, alpha=0.22))
    else:
        for y_slit in [slit_half + gap, -(slit_half + gap)]:
            ax.annotate("", xy=(scr - 0.15, y_slit),
                        xytext=(sx + 0.15, y_slit),
                        arrowprops=dict(arrowstyle="->", color="steelblue", lw=1.4))

    # Detection screen
    ax.plot([scr, scr], [-8.5, 8.5], color="navy", lw=2.0, solid_capstyle="butt")

    # Intensity pattern on screen
    N = 500
    y_draw = np.linspace(-8.2, 8.2, N)
    idx = np.linspace(0, len(I_draw) - 1, N).astype(int)
    I_sampled = I_draw[idx]
    xpat = scr + 1.55 * I_sampled
    color = "firebrick" if waarneming else "royalblue"
    ax.fill_betweenx(y_draw, scr, xpat, alpha=0.45, color=color)
    ax.plot(xpat, y_draw, color="darkorange", lw=1.0)

    plt.tight_layout()
    return fig


def plot_intensity(data, waarneming):
    """Create the intensity pattern plot showing both wave and particle patterns."""
    y_mm = data["y"] * 1e3
    dy_fringe = data["dy_fringe"]

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)

    if waarneming:
        # Active: particle; wave in foreground (solid), particle reference (dashed)
        ax.plot(y_mm, data["I_slit1"], color="grey", lw=1.0, ls="--",
                alpha=0.45, label="Spleet $S_1$")
        ax.plot(y_mm, data["I_slit2"], color="grey", lw=1.0, ls="--",
                alpha=0.45, label="Spleet $S_2$")
        ax.plot(y_mm, data["I_particle"], color="firebrick", lw=1.2, ls="--",
                alpha=0.45, label="Met waarneming")
        ax.fill_between(y_mm, data["I_particle"], alpha=0.07, color="firebrick")
        ax.plot(y_mm, data["I_wave"], color="royalblue", lw=2,
                label="Zonder waarneming")
        ax.fill_between(y_mm, data["I_wave"], alpha=0.20, color="royalblue")
    else:
        # Active: wave (zonder waarneming); reference: particle
        ax.plot(y_mm, data["I_particle"], color="firebrick", lw=1.2, ls="--",
                alpha=0.45, label="Met waarneming")
        ax.fill_between(y_mm, data["I_particle"], alpha=0.07, color="firebrick")
        ax.plot(y_mm, data["I_wave"], color="royalblue", lw=2,
                label="Zonder waarneming")
        ax.fill_between(y_mm, data["I_wave"], alpha=0.20, color="royalblue")

        trans = blended_transform_factory(ax.transData, ax.transAxes)
        ax.annotate("", xy=(dy_fringe / 2 * 1e3, 1.06),
                    xytext=(-dy_fringe / 2 * 1e3, 1.06),
                    xycoords=trans, textcoords=trans,
                    arrowprops=dict(arrowstyle="<->", color="black", lw=1.5),
                    clip_on=False)
        ax.text(0, 1.11,
                rf"$\Delta y = \lambda L/d = {dy_fringe*1e3:.2f}$ mm",
                ha="center", fontsize=10, transform=trans, clip_on=False)

    ax.set_xlabel(r"Positie $y$ (mm)", fontsize=LABEL_FONTSIZE)
    ax.set_ylabel("Intensiteit (rel.)", fontsize=LABEL_FONTSIZE)
    ax.set_xlim(-20, 20)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=LEGEND_FONTSIZE)
    ax.grid(True, alpha=GRID_ALPHA)
    plt.tight_layout(rect=[0, 0, 1, 0.90])
    return fig
