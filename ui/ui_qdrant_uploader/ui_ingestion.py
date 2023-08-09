import streamlit as st

from functions.ingestion import *
def ingestion_context(raw_text, lang):
    file_name = st.session_state.context_file_uploader.name
    collection_name = st.session_state.user + '_docs_' + file_name.split('.')[0]
    PrivateDoc = DocProcessing(raw_text,
                                chunk_size=500,
                                chunk_overlap=200,
                                collection_name=collection_name,
                                book_lang=lang,
                                )
    PrivateDoc.file_processing()
