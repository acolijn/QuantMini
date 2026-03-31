"""Computation and plotting for black-body radiation."""

import numpy as np
import matplotlib.pyplot as plt

from config import H, C, KB, SIGMA, WIEN_B, FIGSIZE_WIDE, LABEL_FONTSIZE, TITLE_FONTSIZE, LEGEND_FONTSIZE, GRID_ALPHA


def planck(lam, T):
    """Spectral radiance via Planck's law [W/m²/sr/m]."""
    return (2 * H * C**2 / lam**5) / (np.exp(H * C / (lam * KB * T)) - 1)


def rayleigh_jeans(lam, T):
    """Classical Rayleigh-Jeans approximation."""
    return 2 * C * KB * T / lam**4


def wien_peak(T):
    """Wavelength of peak emission [m] via Wien's law."""
    return WIEN_B / T


def compute(T, noise=0.05):
    """Return wavelength array and spectral radiance curves."""
    lam_peak = wien_peak(T)
    lam_start = max(50e-9, lam_peak * 0.05)
    lam_end   = max(3000e-9, lam_peak * 5.0)
    lam = np.linspace(lam_start, lam_end, 2000)

    I_planck = planck(lam, T)
    I_rj     = rayleigh_jeans(lam, T)

    # Fake measurement points with Poisson statistics.
    # The noise slider sets the fractional error at the peak (sigma/I_peak = noise).
    # => N_peak = 1/noise^2.  At each wavelength N(lam) = N_peak * I(lam)/I_peak,
    # sigma_N = sqrt(N), so sigma_I = I_peak / sqrt(N_peak) * sqrt(I/I_peak)
    #                               = sqrt(I * I_peak / N_peak)  ∝ sqrt(I)
    rng      = np.random.default_rng()
    lam_meas = np.linspace(lam_start, lam_end, 40)
    I_true   = planck(lam_meas, T)
    I_peak   = I_planck.max()
    N_peak   = max(1, 1.0 / noise**2)          # photons at peak
    I_err    = np.sqrt(I_true * I_peak / N_peak)  # Poisson sigma [W/m²/sr/m]
    I_meas   = I_true + rng.normal(0, 1, len(lam_meas)) * I_err  # scatter ~ sigma

    power = SIGMA * T**4  # total emitted power per unit surface [W/m²]

    return dict(
        lam=lam, I_planck=I_planck, I_rj=I_rj,
        lam_meas=lam_meas, I_meas=I_meas, I_err=I_err, lam_peak=lam_peak, T=T,
        power=power,
    )


def plot_spectrum(data, show_rj=True, show_meas=True, log_scale=False):
    """Plot Planck spectrum, Rayleigh-Jeans, and fake measurement points."""
    d = data
    lam_peak_m = d["lam_peak"]  # metres

    # Choose display unit based on peak wavelength
    use_um = lam_peak_m > 3000e-9  # switch to µm when peak is in mid/far IR
    scale  = 1e6 if use_um else 1e9
    unit   = "µm" if use_um else "nm"

    peak_disp  = lam_peak_m * scale
    lam_disp   = d["lam"]      * scale
    lam_m_disp = d["lam_meas"] * scale

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)

    # Planck
    ax.plot(lam_disp, d["I_planck"] / 1e12,
            color="firebrick", lw=2.5, label="Planck (kwantum)", zorder=3)

    # Rayleigh-Jeans — clamp only in linear mode to avoid huge values
    if show_rj:
        I_rj_plot = d["I_rj"] if log_scale else np.where(
            d["I_rj"] < 5 * d["I_planck"].max(), d["I_rj"], np.nan)
        ax.plot(lam_disp, I_rj_plot / 1e12,
                color="steelblue", lw=2, ls="--",
                label="Rayleigh-Jeans (klassiek)", zorder=2)

    # Fake measurements with error bars
    if show_meas:
        ax.errorbar(lam_m_disp, d["I_meas"] / 1e12,
                    yerr=d["I_err"] / 1e12,
                    fmt="o", color="black", ms=4, lw=0.8,
                    elinewidth=0.8, capsize=2, capthick=0.8,
                    zorder=5, label="Meetpunten")

    # Wien peak annotation
    y_top = 1.3 * d["I_planck"].max() / 1e12
    ax.axvline(peak_disp, color="goldenrod", lw=1, ls=":", alpha=0.8)

    extra_handles = []

    ax.set_xlabel(f"Golflengte λ ({unit})", fontsize=LABEL_FONTSIZE)
    ax.set_ylabel("Spectrale straling (TW/m²/sr/m)", fontsize=LABEL_FONTSIZE)
    ax.set_title(f"T = {data['T']} K",
                 fontsize=TITLE_FONTSIZE)
    ax.set_xlim(lam_disp[0], lam_disp[-1])
    if log_scale:
        ax.set_yscale("log")
        ax.set_ylim(bottom=max(d["I_planck"].max() / 1e12 * 1e-6, 1e-10), top=y_top)
    else:
        ax.set_ylim(0, y_top)

    # Visible light band — rainbow, only relevant in nm mode (380–700 nm)
    # Drawn after ylim is set so extent matches actual axis range
    if not use_um:
        from matplotlib.colors import LinearSegmentedColormap
        rainbow_colors = [
            (0.45, 0.00, 0.80),  # violet  380 nm
            (0.28, 0.00, 1.00),  # indigo  420 nm
            (0.00, 0.00, 1.00),  # blue    450 nm
            (0.00, 0.80, 0.60),  # cyan    490 nm
            (0.00, 0.80, 0.00),  # green   530 nm
            (1.00, 1.00, 0.00),  # yellow  580 nm
            (1.00, 0.50, 0.00),  # orange  620 nm
            (1.00, 0.00, 0.00),  # red     700 nm
        ]
        rainbow_cmap = LinearSegmentedColormap.from_list("vis", rainbow_colors)
        gradient = np.linspace(0, 1, 256).reshape(1, -1)  # violet@380nm left → red@700nm right
        y_lo, y_hi = ax.get_ylim()
        ax.imshow(
            gradient, aspect="auto", cmap=rainbow_cmap, alpha=0.25,
            extent=[380, 700, y_lo, y_hi], zorder=1
        )
        ax.set_ylim(y_lo, y_hi)  # imshow can reset ylim; restore it
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles + extra_handles, [l for l in labels] + [h.get_label() for h in extra_handles], fontsize=LEGEND_FONTSIZE)
    ax.grid(alpha=GRID_ALPHA)
    fig.tight_layout()
    return fig
