import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(page_title="App con Mapas", layout="wide")

with st.sidebar:
    selected = option_menu("Menú", ["Inicio", "Mapa", "Dashboard"],
        icons=["house", "geo-alt", "bar-chart"], menu_icon="cast", default_index=0)

if selected == "Inicio":
    st.title("Bienvenido a la App Interactiva ")
    st.markdown("Esta app tiene mapas, dashboards y está lista para Docker .")
elif selected == "Mapa":
    st.switch_page("pages/1_Mapa.py")
elif selected == "Dashboard":
    st.switch_page("pages/2_Dashboard.py")