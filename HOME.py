import streamlit as st
from ui import *
from functions import *
from PIL import Image

logo = Image.open("./assets/images/logo.png")
st.set_page_config(# Alternate names: setup_page, page, layout
                layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
                initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
                page_title="BookSage",  # String or None. Strings get appended with "• Streamlit". 
                page_icon=logo,  # String, anything supported by st.image, or None.
                )

st.sidebar.success("BookSage")

add_logo()

# --- LOAD CSS ---
with open("./style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
# #-Tabs-Definition----------------------
# tab1, tab2 = st.tabs([
#     "Documents Processing",
#     "Question & Answers",
# ])

# #-Tabs-Custom--------------------------
# with tab1:
#     # st.header("Documents Processing")
#     tab1_main()
#     pass
# with tab2:
#     # st.header("Question & Answers")
#     tab2_main()
    
# ui_chat_messages()

def ui_chat_messages():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input(""):
        st.session_state.messages.append({"role": "user", "content": prompt})
        # prompt = input question
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            # LLM here
            BookQnA = BookQA(llm='palm2',
                        book_lang='en',
                        )
            llm_answer, response_time = BookQnA.bookQnA(prompt)
            # Save to ui response here
            message_placeholder.markdown(llm_answer)
        st.session_state.messages.append({"role": "assistant", "content": llm_answer})