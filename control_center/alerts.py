
import streamlit as st
def alerts_page():
    st.info("This is an informational message.")

    if 'selected_name' in st.session_state:
        st.write(f"Welcome, {st.session_state['selected_name']}!")
    else:
        st.write("No name selected yet.")