"""Streamlit UI for the hydrogen atom orbitals page."""

import matplotlib.pyplot as plt
import streamlit as st

from physics import hydrogen as hy

_ORBITAL_NAMES = {0: "s", 1: "p", 2: "d", 3: "f", 4: "g", 5: "h"}


def render():
    st.title("Waterstof-orbitalen")

    # ── Sidebar controls ──────────────────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Kwantumgetallen")

    n = st.sidebar.slider("Hoofdkwantumgetal n", 1, 6, 1)

    # selectbox prevents Streamlit slider-range errors when n/l changes
    l = st.sidebar.selectbox(
        "Impulsmomentgetal l",
        options=list(range(n)),
        format_func=lambda v: f"{v}  ({_ORBITAL_NAMES.get(v, str(v))})",
    )
    m = st.sidebar.selectbox(
        "Magnetisch kwantumgetal m",
        options=list(range(-l, l + 1)),
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("🧒 Snijvlak")
    plane_type = st.sidebar.radio(
        "Vlak",
        options=["XY  (horizontaal, z=const)", "XZ  (verticaal, y=const)"],
    )
    fixed_axis = "z" if plane_type.startswith("XY") else "y"

    # derive r_max from n without needing data
    r_max_A_ctrl = 0.529 * n * n * 5.0
    step = round(r_max_A_ctrl / 40, 2)
    default_pos  = float(-round(r_max_A_ctrl, 1))   # start at z_min
    plane_pos_A = st.sidebar.slider(
        "Positie snijvlak (\u00c5)",
        min_value=float(-round(r_max_A_ctrl, 1)),
        max_value=float( round(r_max_A_ctrl, 1)),
        value=default_pos,
        step=step,
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ 3D Kwaliteit")
    cross_res = st.sidebar.slider(
        "Doorsnede resolutie", min_value=50, max_value=500, value=250, step=10
    )
    iso_level = st.sidebar.slider(
        "Isovlak drempel (%)", 1, 50, 15, 1
    ) / 100.0

    # ── Derived quantities ────────────────────────────────────────────────
    name      = f"{n}{_ORBITAL_NAMES.get(l, str(l))}"
    E_eV      = -13.6 / n**2
    A0_A      = 0.529  # Bohr radius in Å
    r_mean_A  = A0_A / 2 * (3 * n**2 - l * (l + 1))
    n_radial  = n - l - 1  # number of radial nodes

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Orbitaal", name)
    c2.metric("Energie", f"{E_eV:.3f} eV")
    c3.metric("Gemiddelde straal", f"{r_mean_A:.2f} Å")
    c4.metric("Radiale knopen", str(n_radial))

    # ── Compute ───────────────────────────────────────────────────────────
    with st.spinner("Golffunctie berekenen…"):
        data = hy.compute(n, l, m, resolution=50)

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        "🔮 3D Orbitaal",
        "📊 Doorsnedes",
        "📖 Theorie",
    ])

    with tab1:
        st.markdown(
            "Het **spookisovlak** (blauw, doorschijnend) toont de buitenste "
            "schil van de golffunctie. Het gekleurde **snijvlak** snijdt hier "
            "doorheen en toont |ψ|² op die doorsnede (hot colormap: "
            "zwart = nul, wit = maximum).  "
            "Versleep het **snijvlak** via de zijbalk en **roteer** door op de "
            "grafiek te slepen; **zoom** met het scrollwiel."
        )
        fig3d = hy.plot_orbital_3d(
            data,
            iso_level=iso_level,
            cross_res=cross_res,
            fixed_axis=fixed_axis,
            plane_pos_A=plane_pos_A,
        )
        st.plotly_chart(fig3d, use_container_width=True)

    with tab2:
        st.markdown(
            "Kleurafbeelding van |ψ|² in het **xz-vlak** (y = 0) en het "
            "**xy-vlak** (z = 0).  Witte contourlijnen markeren niveaus van "
            "gelijke kansdichtheid."
        )
        fig2d = hy.plot_orbital_2d(data, res=cross_res)
        st.pyplot(fig2d)
        plt.close(fig2d)

    with tab3:
        col_l, col_r = st.columns([1, 1])
        with col_l:
            st.markdown("### Kwantumgetallen")
            st.markdown(
                "De toestand van het elektron in het waterstofatoom wordt "
                "volledig beschreven door drie kwantumgetallen:\n\n"
                "| Symbool | Naam | Mogelijke waarden |\n"
                "|---------|------|-------------------|\n"
                f"| **n** | hoofdkwantumgetal | 1, 2, 3, … |\n"
                f"| **l** | impulsmomentgetal | 0 … n−1 |\n"
                f"| **m** | magnetisch getal | −l … +l |"
            )
            st.markdown("### Golffunctie")
            st.latex(
                r"\psi_{n l m}(r,\theta,\varphi)"
                r"= R_{nl}(r)\,Y_l^m(\theta,\varphi)"
            )
            st.markdown("**Radiale component** met ρ = 2r / (n a₀):")
            st.latex(
                r"R_{nl}(r) = "
                r"\sqrt{\left(\frac{2}{n a_0}\right)^{\!3}"
                r"\frac{(n-l-1)!}{2n\,(n+l)!}}"
                r"\;e^{-\rho/2}\,\rho^{\,l}\,"
                r"L_{n-l-1}^{2l+1}(\rho)"
            )
            st.markdown(
                "met $L_{n-l-1}^{2l+1}$ de geassocieerde "
                "Laguerre-polynoom."
            )
        with col_r:
            st.markdown("### Energieniveaus")
            st.latex(r"E_n = -\frac{13{,}6\;\text{eV}}{n^2}")
            st.markdown("### Gemiddelde straal")
            st.latex(
                r"\langle r \rangle_{nl}"
                r"= \frac{a_0}{2}\bigl(3n^2 - l(l+1)\bigr)"
            )
            st.markdown("### Kansdictheid")
            st.latex(
                r"|\psi_{nlm}|^2 = |R_{nl}(r)|^2\,|Y_l^m(\theta,\varphi)|^2"
            )
            st.markdown("**Radiale kansdictheid** (kans per eenheid van r):")
            st.latex(r"P(r) = r^2\,|R_{nl}(r)|^2")
            st.markdown("**Aantal radiale knopen:**")
            st.latex(r"n_r = n - l - 1")
            st.markdown("**Hoekknopen** (knooppuntvlakken):")
            st.latex(r"n_\theta = l")
