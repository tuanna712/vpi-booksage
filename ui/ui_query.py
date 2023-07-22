import streamlit as st
from functions import *
def ui_booksage_chat():
    ui_chat_messages()
    pass

def ui_chat_messages():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    refers = None
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
            llm_answer, response_time, refers = BookQnA.bookQnA(prompt)
            # Save to ui response here
            full_response += llm_answer
            message_placeholder.markdown(full_response + "▌")
        st.session_state.messages.append({"role": "assistant", "content": llm_answer})
    
    refer_expander = st.expander("References")
    if refers is not None:
        refers_content:str = ''
        for i in range(len(refers)):
            _chunk_content = refers[i][0].page_content
            try:
                _pdf_name = refers[i][0].metadata["source"].split("/")[-1]
                _ref_page = refers[i][0].metadata["page"]
                refers_content = refers_content + (f"Reference {i+1}: Page {_ref_page} in the file {_pdf_name}: \n{_chunk_content}\n\n")
            except KeyError:
                refers_content = refers_content + (f"Reference {i+1}: \n{_chunk_content}\n\n")
        with refer_expander:
            txt = st.text_area('-',
                               refers_content, 
                               height=300,
                               label_visibility="collapsed",
                               )
            # st.write(txt)    
        