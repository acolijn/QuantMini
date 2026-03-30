"""Streamlit UI for the double-slit experiment page."""

import matplotlib.pyplot as plt
import streamlit as st

from physics import double_slit as ds


def render():
    st.title("Het dubbele-spleten experiment")

    # ── Theory expander ──
    with st.expander("\U0001f4d6 Theorie", expanded=False):
        st.markdown(r"""
Het dubbele-spleten experiment demonstreert **golf-deeltje dualiteit**.
Zonder waarneming bij de spleten zien we een interferentiepatroon;
met waarneming twee pieken.

Intensiteit op het scherm (dubbele spleet + enkelspleet omhullende):

$$I(y) = I_0\left(\frac{\sin\beta}{\beta}\right)^2\cos^2\!\delta$$

met:

$$\beta = \frac{\pi a\, y}{\lambda L},\qquad \delta = \frac{\pi d\, y}{\lambda L}$$

De **fringe-afstand** (afstand tussen maxima) is:

$$\Delta y = \frac{\lambda L}{d}$$

De **de Broglie-golflengte** van een deeltje met massa $m$ en snelheid $v$:

$$\lambda = \frac{h}{mv}$$
        """)

    # ── Sidebar controls ──
    st.sidebar.markdown("---")
    st.sidebar.subheader("\u2699\ufe0f Parameters")

    d_mm = st.sidebar.slider("Spleetafstand d (mm)", 0.05, 0.50, 0.10, 0.05)
    lam_nm = st.sidebar.slider("Golflengte \u03bb (nm)", 400, 700, 500, 10)
    L_m = st.sidebar.slider("Schermafstand L (m)", 0.5, 3.0, 1.0, 0.1)
    a_um = st.sidebar.slider("Spleetbreedte a (\u00b5m)", 10, 100, 30, 5)

    st.sidebar.subheader("\U0001f39b\ufe0f Weergave")
    waarneming = st.sidebar.toggle("Waarneming (deeltjesgedrag)", value=False)

    d = d_mm * 1e-3
    lam = lam_nm * 1e-9
    L = L_m
    a = a_um * 1e-6

    # ── Compute ──
    data = ds.compute(d, lam, L, a)

    # ── Tabs ──
    tab1, tab2 = st.tabs([
        "\U0001f5bc\ufe0f Schematisch overzicht",
        "\U0001f4ca Intensiteitspatroon",
    ])

    with tab1:
        col_fig, col_info = st.columns([2, 1])
        with col_fig:
            fig_s = ds.plot_schema(data, d, lam, L, a, waarneming)
            st.pyplot(fig_s)
            plt.close(fig_s)
        with col_info:
            st.markdown("#### Experimentele parameters")
            st.markdown(f"""
| Parameter | Waarde |
|-----------|--------|
| Spleetafstand $d$ | {d_mm} mm |
| Golflengte $\\lambda$ | {lam_nm} nm |
| Schermafstand $L$ | {L_m} m |
| Spleetbreedte $a$ | {a_um} \u00b5m |
| Fringe-afstand $\\Delta y$ | {data['dy_fringe']*1e3:.3f} mm |
            """)

            if waarneming:
                st.info("\U0001f441\ufe0f **Waarneming aan**: het deeltje gedraagt zich "
                        "als een klassiek deeltje \u2014 twee pieken.")
            else:
                st.success("\U0001f30a **Waarneming uit**: interferentiepatroon "
                           "door golfgedrag.")

    with tab2:
        fig_i = ds.plot_intensity(data, waarneming)
        st.pyplot(fig_i)
        plt.close(fig_i)

        c1, c2, c3 = st.columns(3)
        c1.metric("Fringe-afstand \u0394y", f"{data['dy_fringe'] * 1e3:.3f} mm")
        c2.metric("Golflengte \u03bb", f"{lam_nm} nm")
        c3.metric("Spleetafstand d", f"{d_mm} mm")
