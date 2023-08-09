import os
from PIL import Image
import streamlit as st
from dotenv import load_dotenv

from ui.ui_sidebar import *
from ui.ui_facts_gen import *

# --- SITE SETTING --------------------------------------------------------------
logo = Image.open("./assets/images/logo.png")
st.set_page_config(# Alternate names: setup_page, page, layout
                layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
                initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
                page_title="VPI Sage",  # String or None. Strings get appended with "• Streamlit". 
                page_icon=logo,  # String, anything supported by st.image, or None.
                )
# Add logo to sidebar
# add_logo()
# Add login to sidebar
with st.sidebar:
    login()
# --- LOAD CSS ------------------------------------------------------------------
with open("./style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# --- LOAD .ENV -----------------------------------------------------------------
# Load environment variables from .env file
load_dotenv()
# --- UI MAIN -------------------------------------------------------------------
if 'user_email' in st.session_state and st.session_state.user_email != '':
    FACTS_DB = os.getcwd() + '/' + f'data/{st.session_state.user}/facts'
    os.makedirs(FACTS_DB, exist_ok=True)
    print(FACTS_DB)
    ui_multiple_questions(FACTS_DB)
else:
    st.warning("Please login to continue.")
