"""Streamlit UI for the hydrogen atom orbitals page."""

import math
import matplotlib.pyplot as plt
import streamlit as st

from physics import hydrogen as hy

_ORBITAL_NAMES = {0: "s", 1: "p", 2: "d", 3: "f", 4: "g", 5: "h"}


@st.fragment
def _orbital_3d_tab(data, n, iso_level, cross_res):
    """Fragment: plane-type radio + 3D chart rendered via components.html.

    The plane position slider is a plain HTML range input wired to Plotly.js
    via JavaScript.  Camera save/restore happens in JS after every restyle,
    so zoom is fully preserved client-side with zero Streamlit reruns.
    """
    import json
    import numpy as np
    import streamlit.components.v1 as components

    # ── Plane type ────────────────────────────────────────────────────────
    plane_type = st.radio(
        "Vlak",
        options=["XY  (horizontaal, z=const)", "XZ  (verticaal, y=const)"],
        horizontal=True,
        label_visibility="collapsed",
    )
    fixed_axis = "z" if plane_type.startswith("XY") else "y"

    # ── Positions: neat integer boundary, ~25 steps including 0 Å ─────────
    r_max_A = data["r_max"] * 1e10
    step_raw = 2 * math.ceil(r_max_A) / 24
    if step_raw < 0.375:   step = 0.25
    elif step_raw < 0.75:  step = 0.5
    elif step_raw < 1.5:   step = 1.0
    elif step_raw < 2.5:   step = 2.0
    elif step_raw < 3.5:   step = 3.0
    elif step_raw < 4.5:   step = 4.0
    else:                  step = float(round(step_raw))
    R = float(step * math.ceil(math.ceil(r_max_A) / step))
    positions = [round(float(v), 6) for v in np.arange(-R, R + step * 0.01, step)]
    start_idx = min(range(len(positions)), key=lambda i: abs(positions[i]))

    # ── Build Plotly figure (initial slice) + pre-compute all slices ───────
    fig3d = hy.plot_orbital_3d(
        data,
        iso_level=iso_level,
        cross_res=cross_res,
        fixed_axis=fixed_axis,
        plane_pos_A=positions[start_idx],
    )
    surface_idx = len(fig3d.data) - 1   # surface is always the last trace
    slices = hy.compute_plane_slices(data, fixed_axis, positions, cross_res)

    fig_json    = fig3d.to_json()
    slices_json = json.dumps(slices)
    pos_json    = json.dumps(positions)
    ax_char     = "z" if fixed_axis == "z" else "y"
    height_px   = 660   # figure height set in plot_orbital_3d layout

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
<style>
  body{{margin:0;padding:0;font-family:sans-serif;background:transparent;}}
  #ctrl{{padding:6px 16px 4px;display:flex;align-items:center;gap:10px;}}
  #lbl{{min-width:150px;font-size:13px;}}
  #sld{{flex:1;}}
  #playbtn{{
    font-size:18px;cursor:pointer;border:none;background:transparent;
    padding:0 4px;line-height:1;color:#ccc;
  }}
  #playbtn:hover{{color:#fff;}}
</style></head><body>
<div id="plot"></div>
<div id="ctrl">
  <button id="playbtn" title="Afspelen / pauzeren">▶</button>
  <span id="lbl"></span>
  <input type="range" id="sld" min="0" max="{len(positions)-1}"
         value="{start_idx}" step="1" style="width:100%">
</div>
<script>(function(){{
  var fig       = {fig_json};
  var surfs     = {slices_json};
  var positions = {pos_json};
  var res       = {cross_res};
  var sidx      = {surface_idx};
  var ax        = "{ax_char}";
  var INTERVAL  = 240;   // ms per frame

  Plotly.newPlot('plot', fig.data, fig.layout, {{responsive:true}});

  var sld     = document.getElementById('sld');
  var lbl     = document.getElementById('lbl');
  var playbtn = document.getElementById('playbtn');
  var timer   = null;
  var playing = false;

  function setLabel(posA) {{
    lbl.textContent = 'snijvlak ' + ax + ' = ' + posA.toFixed(1) + ' \u00c5';
  }}
  setLabel(positions[{start_idx}]);

  function flatTo2D(flat, n) {{
    var out = [];
    for (var i = 0; i < n; i++) out.push(flat.slice(i*n, (i+1)*n));
    return out;
  }}
  function constArr(v, n) {{
    var row = new Array(n).fill(v);
    return new Array(n).fill(null).map(function(){{ return row.slice(); }});
  }}

  function showSlice(idx) {{
    sld.value = idx;
    var posA = positions[idx];
    setLabel(posA);
    var gd  = document.getElementById('plot');
    var cam = (gd.layout && gd.layout.scene && gd.layout.scene.camera)
              ? JSON.parse(JSON.stringify(gd.layout.scene.camera)) : null;
    var update = {{ surfacecolor: [flatTo2D(surfs[idx], res)] }};
    update[ax]  = [constArr(posA, res)];
    Plotly.restyle('plot', update, [sidx]).then(function() {{
      if (cam) Plotly.relayout('plot', {{'scene.camera': cam}});
    }});
  }}

  sld.addEventListener('input', function() {{ showSlice(+this.value); }});

  function startPlay() {{
    playing = true;
    playbtn.textContent = '\u23f8';
    timer = setInterval(function() {{
      var next = (+sld.value + 1) % positions.length;
      showSlice(next);
    }}, INTERVAL);
  }}
  function stopPlay() {{
    playing = false;
    playbtn.textContent = '\u25b6';
    clearInterval(timer);
    timer = null;
  }}

  playbtn.addEventListener('click', function() {{
    if (playing) stopPlay(); else startPlay();
  }});
}})();
</script></body></html>"""

    components.html(html, height=height_px + 55, scrolling=False)


@st.cache_data(max_entries=20)
def _cached_compute(n, l, m):
    """Wrapper so the 3D grid is only recomputed when n/l/m changes."""
    return hy.compute(n, l, m, resolution=50)


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
    st.sidebar.subheader("⚙️ 3D Kwaliteit")
    cross_res = st.sidebar.slider(
        "Doorsnede resolutie", min_value=50, max_value=300, value=150, step=10
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
        data = _cached_compute(n, l, m)

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
            "Gebruik de schuifbalk **onder de grafiek** om het snijvlak te verplaatsen; "
            "**roteer** door op de grafiek te slepen; **zoom** met het scrollwiel."
        )
        _orbital_3d_tab(data=data, n=n, iso_level=iso_level, cross_res=cross_res)

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
