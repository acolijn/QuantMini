"""Streamlit UI for the photoelectric effect page."""

import matplotlib.pyplot as plt
import streamlit as st

from config import H, E, METALS
from physics import photoelectric as pe


def render():
    st.title("Het foto-elektrisch effect")

    # ── Theory expander ──
    with st.expander("\U0001f4d6 Theorie", expanded=False):
        st.markdown(r"""
Een foton met energie $E = h\nu$ kan een elektron uit een metaal slaan
als $h\nu > W$ (de werkfunctie).  De kinetische energie van het vrijgekomen
elektron is:

$$E_k = h\nu - W$$

De **stopspanning** is de spanning die nodig is om de stroom tot nul te
reduceren:

$$V_\mathrm{stop} = \frac{h}{e}\,\nu \;-\; \frac{W}{e}$$

De **afkapfrequentie** is de minimale frequentie waarbij foto-emissie optreedt:

$$\nu_c = \frac{W}{h}$$

De helling $h/e$ is **universeel** — onafhankelijk van het metaal.
        """)

    # ── Sidebar controls ──
    st.sidebar.markdown("---")
    st.sidebar.subheader("\u2699\ufe0f Parameters")

    metal = st.sidebar.selectbox(
        "Metaal",
        list(METALS.keys()) + ["Aangepast"],
    )

    if metal == "Aangepast":
        W_eV = st.sidebar.slider("Werkfunctie W (eV)", 1.0, 6.0, 2.3, 0.05)
    else:
        W_eV = METALS[metal]
        st.sidebar.metric("Werkfunctie W", f"{W_eV} eV")

    noise_level = st.sidebar.slider("Meetruis (V)", 0.00, 0.20, 0.04, 0.01)

    st.sidebar.subheader("\U0001f39b\ufe0f Weergave")
    show_extrap = st.sidebar.toggle("Toon extrapolatie", value=True)
    show_fit = st.sidebar.toggle("Toon lineaire fit", value=True)

    # ── Compute ──
    data = pe.compute(W_eV, noise_level)

    # ── Tabs ──
    tab1, tab2 = st.tabs([
        "\U0001f4c8 Stopspanning vs frequentie",
        "\U0001f52c Vergelijking metalen",
    ])

    with tab1:
        metal_label = metal if metal != "Aangepast" else f"W = {W_eV} eV"
        fig1 = pe.plot_main(data, f"Foto-elektrisch effect \u2014 {metal_label}",
                            show_extrap, show_fit)
        st.pyplot(fig1)
        plt.close(fig1)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Afkapfrequentie (theorie)", f'{data["nu_c"]:.3e} Hz')
        c2.metric("Afkapfrequentie (fit)", f'{data["nu_c_fit"]:.3e} Hz')
        c3.metric("h uit fit", f'{data["slope"] * E:.4e} J\u00b7s')
        c4.metric("h (literatuur)", f"{H:.4e} J\u00b7s")

    with tab2:
        fig2 = pe.plot_metals()
        st.pyplot(fig2)
        plt.close(fig2)
