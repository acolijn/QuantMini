"""Streamlit UI for the black-body radiation page."""

import matplotlib.pyplot as plt
import streamlit as st

from physics import blackbody as bb


def render():
    st.title("Zwarte-lichaamsstraling")

    # ── Sidebar controls ──
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Parameters")

    T = st.sidebar.slider("Temperatuur T (K)", 100, 10000, 5778, 100)

    st.sidebar.subheader("🎛️ Weergave")
    show_rj   = st.sidebar.toggle("Toon Rayleigh-Jeans (klassiek)", value=True)
    show_meas = st.sidebar.toggle("Toon meetpunten", value=True)
    log_scale = st.sidebar.toggle("Log schaal (y-as)", value=False)

    # ── Compute ──
    data = bb.compute(T)

    # ── Metrics ──
    lam_peak_nm = data["lam_peak"] * 1e9
    lam_vis = "zichtbaar" if 380 < lam_peak_nm < 700 else (
        "UV" if lam_peak_nm < 380 else "infrarood"
    )

    power_Wm2 = data["power"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Temperatuur", f"{T} K")
    c2.metric("λ_max (Wien)", f"{lam_peak_nm:.0f} nm")
    c3.metric("Kleur piek", lam_vis)
    c4.metric("Uitgestraald vermogen", f"{power_Wm2/1e6:.2f} MW/m²")

    # ── Tabs ──
    tab1, tab2 = st.tabs(["📈 Spectrum", "📖 Theorie"])

    with tab1:
        fig = bb.plot_spectrum(data, show_rj=show_rj, show_meas=show_meas, log_scale=log_scale)
        st.pyplot(fig)
        plt.close(fig)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### De ultravioletcatastrofe")
            st.markdown(
                "De klassieke natuurkunde (Rayleigh-Jeans) voorspelt dat een "
                "heet object oneindig veel energie uitstraalt op korte golflengtes — "
                "de zogenaamde **ultravioletcatastrofe**. Dit klopt totaal niet met "
                "de waarneming.\n\n"
                "**Rayleigh-Jeans:**"
            )
            st.latex(r"B_\lambda^{\rm class}(\lambda,T) = \frac{2ck_BT}{\lambda^4}")
            st.markdown(
                "Deze formule divergeert voor $\\lambda \\to 0$, wat fysisch onmogelijk is."
            )
            st.markdown("### Planck's kwantumhypothese (1900)")
            st.markdown(
                "Max Planck loste dit op door aan te nemen dat energie alleen in "
                "discrete porties (**quanta**) wordt uitgewisseld: $E = h\\nu$."
            )
            st.latex(
                r"B_\lambda(\lambda,T) = "
                r"\frac{2hc^2}{\lambda^5} \cdot \frac{1}{e^{hc/\lambda k_BT}-1}"
            )

        with col2:
            st.markdown("### Wet van Wien")
            st.markdown(
                "De golflengte waarop de straling maximaal is, verschuift met temperatuur:"
            )
            st.latex(r"\lambda_{\rm max} = \frac{b}{T}, \quad b = 2{,}898 \times 10^{-3}\ \text{m K}")
            st.markdown(f"Bij **T = {T} K**: $\\lambda_{{\\rm max}} = {lam_peak_nm:.0f}$ nm")

            st.markdown("### Wet van Stefan-Boltzmann")
            st.markdown(
                "Het totale uitgestraalde vermogen per oppervlakte-eenheid van een zwart lichaam "
                "volgt uit integratie van de Planck-curve over alle golflengtes:"
            )
            st.latex(r"M = \sigma T^4")
            st.markdown("waarbij de Stefan-Boltzmannnconstante $\\sigma$ volledig uitgedrukt kan worden in fundamentele constanten:")
            st.latex(r"\sigma = \frac{2\pi^5 k_B^4}{15\, h^3 c^2} = 5{,}670 \times 10^{-8}\ \text{W m}^{-2}\text{K}^{-4}")
            st.markdown(
                f"Bij **T = {T} K**: $M = {data['power']/1e6:.2f}$ MW/m² — "
                "merk op hoe snel dit groeit met temperatuur ($T^4$)."
            )

            st.markdown("### Constanten")
            st.markdown(
                f"| Constante | Waarde |\n"
                f"|-----------|--------|\n"
                f"| Planckconstante $h$ | $6.626 \\times 10^{{-34}}$ J·s |\n"
                f"| Boltzmannnconstante $k_B$ | $1.381 \\times 10^{{-23}}$ J/K |\n"
                f"| Lichtsnelheid $c$ | $2.998 \\times 10^8$ m/s |\n"
                f"| Wienconstante $b$ | $2.898 \\times 10^{{-3}}$ m·K |"
            )
