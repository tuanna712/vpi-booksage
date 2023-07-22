import chromadb
import pandas as pd
import streamlit as st
from chromadb.utils import embedding_functions
from .ui_ingest_collection import *

def ui_booksage_sidebar():
    # Define basic params
    FACTS_VDB = 'database/user_1/docs_db'
    CLIENT, COHERE_EF = define_globals(FACTS_VDB)
    # Read and call saved collections
    collections_list, collection_namelist = collection_loader(CLIENT)
    collection_name = st.selectbox('Select Collection:', 
                                   collection_namelist, 
                                   key='bs_collection_dropdown')
    
    