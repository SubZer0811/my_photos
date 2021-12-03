import streamlit as st

st.file_uploader("Choose image file(s)", type=[".png", ".jpg", ".jpeg", ".gif", ".tiff"], accept_multiple_files=True)