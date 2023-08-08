# IMPORTING LIBRARIES
import os
from numpy import void
import streamlit as st
import asyncio
# https://frankie567.github.io/httpx-oauth/oauth2/
from httpx_oauth.clients.google import GoogleOAuth2
from dotenv import load_dotenv

load_dotenv('.env')

CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
CLIENT_SECRET = os.environ['GOOGLE_CLIENT_SECRET']
REDIRECT_URI = os.environ['REDIRECT_URI']


async def get_authorization_url(client: GoogleOAuth2, redirect_uri: str):
    authorization_url = await client.get_authorization_url(redirect_uri, scope=["profile", "email"])
    return authorization_url


async def get_access_token(client: GoogleOAuth2, redirect_uri: str, code: str):
    token = await client.get_access_token(code, redirect_uri)
    return token


async def get_email(client: GoogleOAuth2, token: str):
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email


def get_login_str():
    client: GoogleOAuth2 = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)
    authorization_url = asyncio.run(
        get_authorization_url(client, REDIRECT_URI))
    # return f''' < a target = "_self" href = "{authorization_url}" > Google login < /a > '''
    return authorization_url


def get_user() -> void:
    client: GoogleOAuth2 = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)
    # get the code from the url
    code = st.experimental_get_query_params()['code']
    token = asyncio.run(get_access_token(
                        client, REDIRECT_URI, code)
                        )
    st.session_state.user_id, st.session_state.user_email = asyncio.run(
        get_email(client, token['access_token'])
        )
    
def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://i.ibb.co/Jz8CNyh/LogoVPI.png);
                background-repeat: no-repeat;
                background-size: 230px 230px;
                padding-top: 120px;
                padding-left: 10px;
                background-position: 20px 20x;
            }
            [data-testid="stSidebarNav"]::before {
                content: "VPI-Sage";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 100px;
                font: 30px sans-serif;
                color: rgb(186, 38, 15);
                text-align: center;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    