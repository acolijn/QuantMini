"""Streamlit UI for the photoelectric effect page."""

import matplotlib.pyplot as plt
import streamlit as st

from config import H, E, METALS
from physics import photoelectric as pe


def render():
    st.title("Het foto-elektrisch effect")

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
    tab1, tab2, tab3 = st.tabs([
        "\U0001f4c8 Stopspanning vs frequentie",
        "\U0001f52c Vergelijking metalen",
        "\U0001f4d6 Theorie",
    ])

    with tab1:
        metal_label = metal if metal != "Aangepast" else f"W = {W_eV} eV"
        fig1 = pe.plot_main(data, f"{metal_label}",
                            show_extrap, show_fit)
        st.pyplot(fig1)
        plt.close(fig1)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Afkapfrequentie (theorie)",
                  f'{data["nu_c"]:.3e} Hz  /  {3e8/data["nu_c"]*1e9:.0f} nm')
        c2.metric("Afkapfrequentie (fit)",
                  f'{data["nu_c_fit"]:.3e} Hz  /  {3e8/data["nu_c_fit"]*1e9:.0f} nm')
        c3.metric("h uit fit", f'{data["slope"] * E:.4e} J\u00b7s')
        c4.metric("h (literatuur)", f"{H:.4e} J\u00b7s")

    with tab2:
        fig2 = pe.plot_metals()
        st.pyplot(fig2)
        plt.close(fig2)

    with tab3:
        col_l, col_r = st.columns([1, 1])
        with col_l:
            st.markdown("### Het foto-elektrisch effect")
            st.markdown(
                "In 1905 verklaarde Einstein dat licht bestaat uit "
                "energiepakketten (**fotonen**). Een foton met frequentie "
                r"$\nu$ draagt energie:"
            )
            st.latex(r"E = h\nu")
            st.markdown(
                r"Als $E > W$ (de werkfunctie van het metaal) kan het foton "
                "een elektron vrijslaan. De resterende energie wordt kinetische "
                "energie van het elektron:"
            )
            st.latex(r"E_k = h\nu - W")
            st.markdown(
                r"De werkfunctie $W$ is de minimale energie die nodig is om "
                "een elektron los te maken van het metaaloppervlak."
            )
        with col_r:
            st.markdown("### Stopspanning")
            st.markdown(
                r"De **stopspanning** $V_\mathrm{stop}$ is de tegenspanning "
                "die nodig is om alle elektronen tegen te houden:"
            )
            st.latex(r"V_\mathrm{stop} = \frac{h}{e}\,\nu - \frac{W}{e}")
            st.markdown(
                r"Dit is een lineaire functie van $\nu$. De helling $h/e$ is "
                "**universeel** — onafhankelijk van het metaal. "
                r"Zo kan men $h$ experimenteel bepalen."
            )
            st.markdown("### Afkapfrequentie")
            st.markdown(
                "Beneden de **afkapfrequentie** treedt geen foto-emissie op, "
                "hoe helder het licht ook is:"
            )
            st.latex(r"\nu_c = \frac{W}{h}")
            st.markdown("### Constanten")
            st.markdown(f"""
| Grootheid | Waarde |
|-----------|--------|
| Planck-constante $h$ | $6.626 \\times 10^{{-34}}$ J·s |
| Elementaire lading $e$ | $1.602 \\times 10^{{-19}}$ C |
| $h/e$ (helling) | $4.136 \\times 10^{{-15}}$ V·s |
| Werkfunctie huidig metaal | {W_eV} eV |
            """)
