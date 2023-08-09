import streamlit as st


def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://i.ibb.co/Jz8CNyh/LogoVPI.png);
                background-repeat: no-repeat;
                background-size: 180px 180px;
                padding-top: 120px;
                padding-left: 05px;
                background-position: 0px 0px 20px 20x;
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

# --- LOGIN ---------------------------------------------------------------------
def login():
    st.text_input(label='Enter your email:',
                key='user_email')
    if 'user_email' in st.session_state and st.session_state.user_email != '':
        st.session_state.user = st.session_state.user_email.split("@")[0]
        st.success(f'Logged in as: {st.session_state.user}')
