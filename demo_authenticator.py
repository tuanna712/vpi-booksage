import streamlit as st
from msal_streamlit_authentication import msal_authentication


login_token = msal_authentication(
    auth={
        "clientId": "d0f682f2-6d52-4160-96ba-e44272dffd47",
        "authority": "https://login.microsoftonline.com/c5ec5abe-76c1-46cb-b3fe-c3b0071ffdb3",
        "redirectUri": "http://localhost:8501/",
        "postLogoutRedirectUri": "http://localhost:8501//"
    }, # Corresponds to the 'auth' configuration for an MSAL Instance
    cache={
        "cacheLocation": "sessionStorage",
        "storeAuthStateInCookie": False
    }, # Corresponds to the 'cache' configuration for an MSAL Instance
    login_request={
        "scopes": ["d0f682f2-6d52-4160-96ba-e44272dffd47/.default"]
    }, # Optional
    logout_request={}, # Optional
    login_button_text="Login", # Optional, defaults to "Login"
    logout_button_text="Logout", # Optional, defaults to "Logout"
    class_name="css_button_class_selector", # Optional, defaults to None. Corresponds to HTML class.
    html_id="html_id_for_button", # Optional, defaults to None. Corresponds to HTML id.
    key=1 # Optional if only a single instance is needed
)
st.write("Recevied login token:", login_token)