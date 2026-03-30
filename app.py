"""
Quantum Physics Interactive Web App
====================================
Run with:  streamlit run app.py
"""

import streamlit as st

st.set_page_config(page_title="Kwantumfysica", page_icon="\u269b\ufe0f", layout="wide")

# ── Sidebar navigation ───────────────────────────────────────────────────────
st.sidebar.title("\u269b\ufe0f Kwantumfysica")
page = st.sidebar.radio(
    "Kies een experiment",
    ["Foto-elektrisch effect", "Dubbele-spleet experiment"],
)

# ── Page routing ──────────────────────────────────────────────────────────────
if page == "Foto-elektrisch effect":
    from views.photoelectric import render
    render()
else:
    from views.double_slit import render
    render()
