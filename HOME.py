import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from PIL import Image
import streamlit as st
from dotenv import load_dotenv
from msal_streamlit_authentication import msal_authentication

from functions.sharePointConnector import *
from functions.auth import *
# from ui.ui_ingestion import *
# from ui.ui_ingest_collection import *
# from ui.ui_query import *
# from ui.ui_booksage import *

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
user_name = st.text_input(label='Enter your email:',
            value='vpi_user_name@vpi.pvn.vn',
            key='defined_email')
st.session_state.user_email = user_name
# --- LOGIN ---------------------------------------------------------------------
# from httpx_oauth.oauth2 import GetAccessTokenError
# if 'user_email' not in st.session_state:
#     url = get_login_str()
#     st.write(f'''<div style="text-align: center;">
#   <h5>
#     Login: <a target="_self" href="{url}">Google</a>
#   </h5>
# </div>
# ''',
#             unsafe_allow_html=True)
#     if st.button("User Information", key="display_user"):
#         try:
#             get_user()
#         except GetAccessTokenError:
#             st.warning("Please login first")
# if 'user_email' in st.session_state:
#     st.write(f"Welcome {st.session_state.user_email}")
# else:
#     st.warning("Please login first")
#     st.stop()

# --- MSAL AUTHENTICATION ------------------------------------------------------------------
# login_token = msal_authentication(
#     auth={
#         "clientId": "d0f682f2-6d52-4160-96ba-e44272dffd47",
#         "authority": "https://login.microsoftonline.com/c5ec5abe-76c1-46cb-b3fe-c3b0071ffdb3",
#         "redirectUri": "https://vpisage.azurewebsites.net/",
#         "postLogoutRedirectUri": "https://vpisage.azurewebsites.net//"
#     }, # Corresponds to the 'auth' configuration for an MSAL Instance
#     cache={
#         "cacheLocation": "sessionStorage",
#         "storeAuthStateInCookie": False
#     }, # Corresponds to the 'cache' configuration for an MSAL Instance
#     login_request={
#         "scopes": ["d0f682f2-6d52-4160-96ba-e44272dffd47/.default"]
#     }, # Optional
#     logout_request={}, # Optional
#     login_button_text="Login", # Optional, defaults to "Login"
#     logout_button_text="Logout", # Optional, defaults to "Logout"
#     class_name="css_button_class_selector", # Optional, defaults to None. Corresponds to HTML class.
#     html_id="html_id_for_button", # Optional, defaults to None. Corresponds to HTML id.
#     key=1 # Optional if only a single instance is needed
# )
# st.write("Recevied login token:", login_token)

# --- SYNCHRONIZE ---------------------------------------------------------------------
if 'user_email' in st.session_state:
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
        
        


