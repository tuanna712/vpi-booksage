import streamlit as st
from functions import *
def tab2_main():
    # question_form = st.form('question')
    # with question_form:
    #     question = st.text_input('Question here!', key='question')
    #     _btn = question_form.form_submit_button('Summit')
    # if _btn:
    #     BookQnA = BookQA(llm='palm2',
    #                     book_lang='en',
    #                     )
    #     llm_answer, response_time = BookQnA.bookQnA(question)
    #     st.write(llm_answer)

    ui_chat_messages()
    pass

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
            full_response = ""
            # LLM here
            BookQnA = BookQA(llm='chatgpt',
                        book_lang='en',
                        )
            llm_answer, response_time = BookQnA.bookQnA(prompt)
            # Save to ui response here
            full_response += llm_answer
            message_placeholder.markdown(full_response + "▌")
        st.session_state.messages.append({"role": "assistant", "content": llm_answer})