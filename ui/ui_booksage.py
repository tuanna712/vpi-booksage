import chromadb
import pandas as pd
import streamlit as st
from chromadb.utils import embedding_functions
from ui_ingest_collection import *
import time

def ui_booksage_sidebar():
    with st.sidebar:
        if 'user_email' in st.session_state:
            st.write(f"User email: {st.session_state.user_email}")
            USER = st.session_state.user_email.split('@')[0]
            st.session_state.user = USER
            
        else:
            st.warning("Please login first")
            st.stop()
        # Define basic params
        FACTS_VDB = f'database/{USER}/docs_db'
        st.session_state.FACTS_VDB = FACTS_VDB
        CLIENT, COHERE_EF = define_globals(FACTS_VDB)
        # Read and call saved collections
        collections_list, collection_namelist = collection_loader(CLIENT)
        collection_name = st.selectbox(label='Select Collection:', 
                                    options=collection_namelist, 
                                    key='bs_collection_dropdown')
        # Select Book Language
        book_lang = st.radio(label='Select Book Language:',
                                 options=['ENG', 'VIE'],
                                 key='bs_book_lang_selected')
        # Select LLM
        llm = st.radio(label='Select LLM:',
                        options=['OPENAI 3.5', 'GOOGLE PALM 2', 'CLAUDE'],
                        key='bs_llm_selected')
        # Select Top k
        top_k = st.slider(label='Select Top k:',
                          min_value=1, max_value=10,
                          value=5, key='bs_top_k_selected')
    