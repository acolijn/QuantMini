"""Streamlit UI for the double-slit experiment page."""

import matplotlib.pyplot as plt
import streamlit as st

from physics import double_slit as ds


def render():
    st.title("Het dubbele-spleten experiment")

    # ── Sidebar controls ──
    st.sidebar.markdown("---")
    st.sidebar.subheader("\u2699\ufe0f Parameters")

    d_mm = st.sidebar.slider("Spleetafstand d (mm)", 0.05, 0.50, 0.10, 0.05)
    lam_nm = st.sidebar.slider("Golflengte \u03bb (nm)", 400, 700, 500, 10)
    L_m = st.sidebar.slider("Schermafstand L (m)", 0.5, 3.0, 1.0, 0.1)
    a_um = st.sidebar.slider("Spleetbreedte a (\u00b5m)", 10, 100, 30, 5)

    d = d_mm * 1e-3
    lam = lam_nm * 1e-9
    L = L_m
    a = a_um * 1e-6

    # ── Compute ──
    data = ds.compute(d, lam, L, a)

    # ── Tabs ──
    tab1, tab2 = st.tabs([
        "\U0001f4ca Intensiteitspatroon",
        "\U0001f4d6 Theorie",
    ])

    with tab2:
        col_l, col_r = st.columns([1, 1])
        with col_l:
            st.markdown("### Golf-deeltje dualiteit")
            st.markdown(
                "Richard Feynman noemde het dubbele-spleten experiment "
                "'het enige mysterie van de kwantummechanica'. "
                "Zonder waarneming bij de spleten gedraagt een deeltje "
                "zich als een golf en ontstaat een **interferentiepatroon**. "
                "Zodra we meten door welke spleet het deeltje gaat, "
                "verdwijnt de interferentie en zien we twee klassieke pieken."
            )
            st.markdown("### Intensiteitspatroon")
            st.markdown(
                "De intensiteit op het scherm is het product van de "
                "enkelspleet-omhullende en de dubbelspleet-cosinusfactor:"
            )
            st.latex(
                r"I(y) = I_0\left(\frac{\sin\beta}{\beta}\right)^2\cos^2\!\delta"
            )
            st.markdown("met")
            st.latex(
                r"\beta = \frac{\pi a\, y}{\lambda L}, \qquad"
                r"\delta = \frac{\pi d\, y}{\lambda L}"
            )
            st.markdown(
                r"waarbij $a$ de spleetbreedte, $d$ de spleetafstand en "
                r"$L$ de afstand tot het scherm is."
            )
        with col_r:
            st.markdown("### Fringe-afstand")
            st.markdown(
                "De afstand tussen opeenvolgende heldere maxima (fringes) is:"
            )
            st.latex(r"\Delta y = \frac{\lambda L}{d}")
            st.markdown(
                r"Een **grotere golflengte** of **grotere schermafstand** "
                r"geeft bredere fringes; een **grotere spleetafstand** "
                r"geeft smallere fringes."
            )
            st.markdown("### De Broglie-golflengte")
            st.markdown(
                "Ook massieve deeltjes (elektronen, neutronen, moleculen) "
                "hebben een golflengte:"
            )
            st.latex(r"\lambda = \frac{h}{mv}")
            st.markdown(
                r"met $h = 6.626 \times 10^{-34}$ J·s de constante van Planck, "
                r"$m$ de massa en $v$ de snelheid van het deeltje."
            )
            st.markdown("### Actuele parameterwaarden")
            st.markdown(f"""
| Parameter | Waarde |
|-----------|--------|
| Spleetafstand $d$ | {d_mm} mm |
| Golflengte $\\lambda$ | {lam_nm} nm |
| Schermafstand $L$ | {L_m} m |
| Spleetbreedte $a$ | {a_um} µm |
| Fringe-afstand $\\Delta y$ | {data['dy_fringe']*1e3:.3f} mm |
            """)

    with tab1:
        sch_l, sch_r = st.columns(2)
        with sch_l:
            fig_s0 = ds.plot_schema(data, d, lam, L, a, waarneming=False)
            st.pyplot(fig_s0, use_container_width=False)
            plt.close(fig_s0)
        with sch_r:
            fig_s1 = ds.plot_schema(data, d, lam, L, a, waarneming=True)
            st.pyplot(fig_s1, use_container_width=False)
            plt.close(fig_s1)

        fig_i = ds.plot_intensity(data, False)
        st.pyplot(fig_i)
        plt.close(fig_i)

        c1, c2, c3 = st.columns(3)
#        c1.metric("Fringe-afstand \u0394y", f"{data['dy_fringe'] * 1e3:.3f} mm")
        c1.metric("Fringe-afstand $\Delta y$", f"{data['dy_fringe'] * 1e3:.3f} mm")
        c2.metric("Golflengte \u03bb", f"{lam_nm} nm")
        c3.metric("Spleetafstand d", f"{d_mm} mm")
