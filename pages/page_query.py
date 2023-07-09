import streamlit as st
from functions import *
from ui import *

# --- LOAD CSS ---
with open("./style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
tab2_main()