"""Computation and plotting for the double-slit experiment."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from config import FIGSIZE_WIDE, FIGSIZE_SCHEMA, LABEL_FONTSIZE, TITLE_FONTSIZE, LEGEND_FONTSIZE, GRID_ALPHA


def compute(d, lam, L, a):
    """Compute intensities for the double-slit experiment."""
    y_max_m = 4 * lam * L / d
    y = np.linspace(-y_max_m, y_max_m, 2000)

    beta = np.pi * a * y / (lam * L)
    delta = np.pi * d * y / (lam * L)
    sinc = np.where(np.abs(beta) < 1e-10, 1.0, np.sin(beta) / beta)

    I_wave = (sinc * np.cos(delta)) ** 2
    I_wave /= I_wave.max()

    sigma = 0.8 * lam * L / a
    I_particle = (np.exp(-0.5 * ((y - d / 2) / sigma) ** 2)
                  + np.exp(-0.5 * ((y + d / 2) / sigma) ** 2))
    I_particle /= I_particle.max()

    dy_fringe = lam * L / d

    return dict(
        y=y, I_wave=I_wave, I_particle=I_particle, dy_fringe=dy_fringe,
    )


def plot_schema(data, d, lam, L, a, waarneming):
    """Create the schematic side-view figure of the double-slit setup."""
    I_draw = data["I_particle"] if waarneming else data["I_wave"]

    fig, ax = plt.subplots(figsize=FIGSIZE_SCHEMA)
    ax.set_xlim(0, 12)
    ax.set_ylim(-9.5, 9.5)
    ax.set_aspect("equal")
    ax.axis("off")

    title = ("Met waarneming (deeltjesgedrag)"
             if waarneming else "Zonder waarneming (golfgedrag)")
    ax.set_title(title, fontsize=TITLE_FONTSIZE, fontweight="bold")

    # Source
    ax.add_patch(patches.Circle((0.7, 0), 0.42, color="gold",
                                ec="darkorange", lw=1.5, zorder=5))
    for ang in np.linspace(-0.45, 0.45, 5):
        dx, dy = np.cos(ang), np.sin(ang)
        ax.annotate("", xy=(0.7 + 1.0 * dx, dy),
                     xytext=(0.7 + 0.45 * dx, 0.45 * dy),
                     arrowprops=dict(arrowstyle="->", color="goldenrod", lw=1.2))
    ax.text(0.7, -1.05, "bron", ha="center", fontsize=9, color="darkorange")

    # Slit screen
    sx = 4.5
    slit_half = 1.1
    gap = 0.3
    for y0, y1 in [(-8.5, -(slit_half + gap)),
                    (-(slit_half - gap), (slit_half - gap)),
                    ((slit_half + gap), 8.5)]:
        ax.plot([sx, sx], [y0, y1], color="#333333", lw=8, solid_capstyle="butt")
    ax.text(sx - 0.55, slit_half + gap + 0.4, r"$S_1$", ha="right", fontsize=11)
    ax.text(sx - 0.55, -(slit_half + gap + 0.4), r"$S_2$", ha="right", fontsize=11)

    # Detector (if observing)
    if waarneming:
        ax.add_patch(patches.FancyBboxPatch(
            (sx + 0.2, 0.75), 1.15, 0.7,
            boxstyle="round,pad=0.1",
            facecolor="#d0e8ff", edgecolor="navy", lw=1.8, zorder=6))
        ax.text(sx + 0.775, 1.12, "\U0001f441\ufe0f",
                ha="center", fontsize=13, va="center", zorder=7)
        ax.text(sx + 0.775, 0.72, "detector",
                ha="center", fontsize=7.5, color="navy", va="top", zorder=7)

    # Rays
    scr = 10.3
    if not waarneming:
        for y_slit in [slit_half + gap, -(slit_half + gap)]:
            for frac in np.linspace(-0.55, 0.55, 9):
                y_end = y_slit + frac * 6.5
                ax.annotate("", xy=(scr - 0.15, y_end),
                            xytext=(sx + 0.15, y_slit),
                            arrowprops=dict(arrowstyle="->", color="steelblue",
                                            lw=0.7, alpha=0.28))
    else:
        for y_slit in [slit_half + gap, -(slit_half + gap)]:
            ax.annotate("", xy=(scr - 0.15, y_slit),
                        xytext=(sx + 0.15, y_slit),
                        arrowprops=dict(arrowstyle="->", color="steelblue", lw=2.0))

    # Detection screen
    ax.plot([scr, scr], [-8.5, 8.5], color="navy", lw=5.5, solid_capstyle="butt")

    # Intensity pattern on screen
    N = 500
    y_draw = np.linspace(-8.2, 8.2, N)
    idx = np.linspace(0, len(I_draw) - 1, N).astype(int)
    I_sampled = I_draw[idx]
    xpat = scr + 1.55 * I_sampled
    color = "firebrick" if waarneming else "royalblue"
    ax.fill_betweenx(y_draw, scr, xpat, alpha=0.45, color=color)
    ax.plot(xpat, y_draw, color="darkorange", lw=1.5)

    plt.tight_layout()
    return fig


def plot_intensity(data, waarneming):
    """Create the intensity pattern plot."""
    y_mm = data["y"] * 1e3
    dy_fringe = data["dy_fringe"]

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)

    if waarneming:
        ax.plot(y_mm, data["I_particle"], color="firebrick", lw=2,
                label="Met waarneming (deeltjes)")
        ax.fill_between(y_mm, data["I_particle"], alpha=0.20, color="firebrick")
    else:
        ax.plot(y_mm, data["I_wave"], color="royalblue", lw=2,
                label="Zonder waarneming (golf)")
        ax.fill_between(y_mm, data["I_wave"], alpha=0.20, color="royalblue")

        ax.annotate("", xy=(dy_fringe / 2 * 1e3, 0.75),
                    xytext=(-dy_fringe / 2 * 1e3, 0.75),
                    arrowprops=dict(arrowstyle="<->", color="black", lw=1.5))
        ax.text(0, 0.82,
                rf"$\Delta y = \lambda L/d = {dy_fringe*1e3:.2f}$ mm",
                ha="center", fontsize=10)

    ax.set_xlabel(r"Positie $y$ (mm)", fontsize=LABEL_FONTSIZE)
    ax.set_ylabel("Intensiteit (rel.)", fontsize=LABEL_FONTSIZE)
    ax.set_ylim(0, 1.12)
    ax.legend(fontsize=LEGEND_FONTSIZE)
    ax.grid(True, alpha=GRID_ALPHA)
    plt.tight_layout()
    return fig
