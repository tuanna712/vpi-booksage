import pandas as pd
import streamlit as st

import cohere, os
from qdrant_client import QdrantClient

from langchain.schema import Document
from langchain.vectorstores import Qdrant
from langchain.embeddings import CohereEmbeddings

from dotenv import load_dotenv
load_dotenv()

def collection_management(FACTS_VDB):
    # Define basic params
    client, embeddings = define_globals(FACTS_VDB)
    # Read and call saved collections
    st.session_state.collection_namelist = [client.get_collections().collections[i].name for i in range(len(client.get_collections().collections))]
    collection_name = st.selectbox('Select Collection:', 
                                   st.session_state.collection_namelist, 
                                   key='rv_collection_dropdown')
    
    # Read single collection
    read_single_collection(client, collection_name)

# Define GLOBALS ---------------------------------------------------------------
def define_globals(FACTS_VDB):
    embeddings = CohereEmbeddings(model="multilingual-22-12", 
                                cohere_api_key=os.environ['COHERE_API_KEY'])
    qdrant_url = os.environ['QDRANT_URL']
    qdrant_api_key = os.environ['QDRANT_API_KEY']
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    return client, embeddings
    
# Call Collection ---------------------------------------------------------------
def read_single_collection(client, COHERE_EF, collections_list, collection_name):
    # Get collection
    if len(collections_list) > 0 and collection_name is not None:
        query_collection = client.get_collection(name = collection_name, 
                                                embedding_function = COHERE_EF)
        # Write collection information
        st.write(query_collection)
        # Review collection documents
        len_docs = len(query_collection.get()['documents'])
        st.write(f'Number of documents: {len_docs}')
        if len_docs > 0:
            # Docs selection
            doc_selection = st.number_input(label='Document ID:', 
                                            min_value=0, max_value=len_docs-1,
                                            value=0, key='doc_selection')
            # Display document by ID
            st.write(query_collection.get()['documents'][doc_selection].replace('_', ' '))
            # Display metadata of document
            metadata = query_collection.get()['metadatas'][doc_selection]
            if len(metadata) > 0:
                st.write(f'Page information: {metadata}')
        else:
            st.info('No available documents')
            
def remove_collection(FACTS_VDB):
    # Define basic params
    client, embeddings = define_globals(FACTS_VDB)
    # Define removing collection name
    collection_name = st.selectbox('Select Collection:', 
                                   st.session_state.collection_namelist, 
                                   key='remove_collection_dropdown')
    
    # Button to delete a collection
    if st.button('Delete Collection', key='rm_collection_btn'):
        client.delete_collection(collection_name=st.session_state.remove_collection_dropdown)
        st.experimental_rerun()

def title_ui(title):
    st.write(f'''<div style="text-align: center;">
                <h5 style="color: #1D5B79;
                            font-size: 40px;
                            font-weight: bold;
                ">{title}</h5>
                </div>
            ''',
                unsafe_allow_html=True)
    

    
