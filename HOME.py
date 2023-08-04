import streamlit as st
from ui import *
from .functions.auth import *
from .functions.sharePointConnector import *
from PIL import Image
from dotenv import load_dotenv
import os

logo = Image.open("./assets/images/logo.png")
st.set_page_config(# Alternate names: setup_page, page, layout
                layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
                initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
                page_title="VPI Sage",  # String or None. Strings get appended with "• Streamlit". 
                page_icon=logo,  # String, anything supported by st.image, or None.
                )
# Add logo to sidebar
add_logo()

# --- LOAD CSS ------------------------------------------------------------------
with open("./style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- LOAD .ENV -----------------------------------------------------------------
# Load environment variables from .env file
load_dotenv()

CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
CLIENT_SECRET = os.environ['GOOGLE_CLIENT_SECRET']
REDIRECT_URI = os.environ['REDIRECT_URI']

# --- LOGIN ---------------------------------------------------------------------
from httpx_oauth.oauth2 import GetAccessTokenError
if 'user_email' not in st.session_state:
    url = get_login_str()
    st.write(f'''<div style="text-align: center;">
  <h5>
    Login: <a target="_self" href="{url}">Google</a>
  </h5>
</div>
''',
            unsafe_allow_html=True)
    if st.button("User Information", key="display_user"):
        try:
            get_user()
        except GetAccessTokenError:
            st.warning("Please login first")
if 'user_email' in st.session_state:
    st.write(f"Welcome {st.session_state.user_email}")
else:
    st.warning("Please login first")
    st.stop()

# --- API KEY IMPORT ------------------------------------------------------------------
# password = st.text_input("Enter a password", type="password")

# --- SYNCHRONIZE ---------------------------------------------------------------------
userSync = DatabaseLink(st.session_state.user_email)
st.write(f"User: {userSync.username}")
_home_columns = st.columns(2)
with _home_columns[0]:
    upload = st.button("Sync Upload", key="sync_upload")
with _home_columns[1]:
    download = st.button("Sync Download", key="sync_download")

if upload:
    with st.spinner('Uploading...'):
        userSync.upload_overwrite()
    st.success("Upload successfully")
    
if download:
    with st.spinner('Downloading...'):
        userSync.download_overwrite()
    st.success("Download successfully")