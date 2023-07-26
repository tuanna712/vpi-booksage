import streamlit as st
from functions import *
from ui import *
from PIL import Image

# add_logo()

logo = Image.open("./assets/images/logo.png")
st.set_page_config(# Alternate names: setup_page, page, layout
                layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
                initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
                page_title="VPI Sage",  # String or None. Strings get appended with "• Streamlit". 
                page_icon=logo,  # String, anything supported by st.image, or None.
                )
# --- LOAD CSS ---------------------------------------------------------------
with open("./style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# Display title
title_ui('COLLECTIONS')
# Sidebar settings -----------------------------------------------------------
ui_sidebar_ingestion()
# --- TABS Definition ---------------------------------------------------------------
_tab_create, _tab_review, _tab_remove = st.tabs(['Create Collection', 
                                                 'Review Collection',
                                                 'Remove Collection'
                                                 ])
# Check if user is logged in------------------------
if 'user_email' in st.session_state:
    USER = st.session_state.user_email.split('@')[0]
    FACTS_VDB = f'database/{USER}/docs_db'
else:
    st.warning("Please login first")
    st.stop()
# --- Create Collection ----------------------------
with _tab_create:
    ingestion_params(FACTS_VDB)
# --- Manage Collection ----------------------------
with _tab_review:
    collection_management(FACTS_VDB)
# --- Remove Collection ----------------------------
with _tab_remove:
    remove_collection(FACTS_VDB)