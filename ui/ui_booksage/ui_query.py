import streamlit as st
from functions.query import *

def ui_booksage_chat():
    if 'bs_collection_dropdown' in st.session_state:
        collection_name = st.session_state.bs_collection_dropdown
    if 'bs_book_lang_selected' in st.session_state:
        book_lang = st.session_state.bs_book_lang_selected
        if book_lang == 'ENG':
            book_lang = 'en'
        else:
            book_lang = 'vi'
    if 'bs_llm_selected' in st.session_state:
        llm = st.session_state.bs_llm_selected
        if llm == 'OPENAI 3.5':
            llm = 'openai'
        elif llm == 'GOOGLE PALM 2':
            llm = 'palm2'
        elif llm == 'CLAUDE':
            llm = 'claude'
    if 'bs_top_k_selected' in st.session_state:
        top_k = st.session_state.bs_top_k_selected
    
    ui_chat_messages(collection_name, book_lang, llm, top_k)
    pass

def ui_chat_messages(collection_name, book_lang, llm, top_k):
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
            BookQnA = BookQA(llm=llm,
                        # vector_path=st.session_state.FACTS_VDB,
                        user=st.session_state.user,
                        book_lang=book_lang,
                        collection_name=collection_name,
                        top_k_searching=top_k,
                        )
            with st.spinner(text='Responding...'):
                _llm_answer, st.session_state.response_time, refers = BookQnA.bookQnA(prompt)
            # Save to ui response here
            full_response += _llm_answer
            message_placeholder.markdown(full_response + "▌")
        st.session_state.messages.append({"role": "assistant", "content": _llm_answer})
    
    refer_expander = st.expander("References")
    try:
        if refers[0] == 'faq':
            with refer_expander:
                st.info('This is a FAQ.')
        elif refers is not None:
            refers_content:str = ''
            for i in range(len(refers)):
                if book_lang == 'vi':
                    _chunk_content = refers[i][0].page_content.replace("_", " ")
                else:
                    _chunk_content = refers[i][0].page_content
                try:
                    _pdf_name = refers[i][0].metadata["source"].split("/")[-1]
                    _ref_page = refers[i][0].metadata["page"]
                    refers_content = refers_content + (f"Reference {i+1}: Page {_ref_page} in the file {_pdf_name}: \n{_chunk_content}\n\n")
                except KeyError:
                    refers_content = refers_content + (f"Reference {i+1}: \n{_chunk_content}\n\n")
            with refer_expander:
                txt = st.text_area('-',
                                (f'Response time: {round(st.session_state.response_time.total_seconds(),2)} seconds\n\n{refers_content}'), 
                                height=300,
                                label_visibility="collapsed",
                                )
    except TypeError:
        pass
        