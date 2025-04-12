import streamlit as st

def show_sidebar():
    with st.sidebar:
        st.title("NIDS Controls")
        st.slider("Detection Threshold", 0.0, 1.0, 0.8, key="threshold")
        st.number_input("Update Interval (sec)", 1, 60, 5, key="interval")
        st.selectbox("View Mode", ["Standard", "Expert"], key="view_mode")
