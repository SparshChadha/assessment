import streamlit as st

def initialize_session_state():
    if 'data' not in st.session_state:
        st.session_state.data = None