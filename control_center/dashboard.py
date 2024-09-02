import streamlit as st
import folium
from streamlit_folium import st_folium

def dashboard_page():
    # Button to navigate to the Alerts page
    st.link_button("Alerts link",url="/")
    if st.button("Go to Alerts"):
        st.session_state['page_name'] = "Alerts"

