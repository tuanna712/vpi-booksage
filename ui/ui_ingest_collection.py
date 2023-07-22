import chromadb
import pandas as pd
import streamlit as st
from chromadb.utils import embedding_functions


def collection_management():
    # Define basic params
    FACTS_VDB = 'database/user_1/docs_db'
    CLIENT, COHERE_EF = define_globals(FACTS_VDB)
    # Read and call saved collections
    collections_list, collection_namelist = collection_loader(CLIENT)
    collection_name = st.selectbox('Select Collection:', 
                                   collection_namelist, 
                                   key='rv_collection_dropdown')
    
    # Read single collection
    read_single_collection(CLIENT, COHERE_EF, collections_list, collection_name)
    
def remove_collection():
    # Define basic params
    FACTS_VDB = 'database/user_1/docs_db'
    CLIENT, COHERE_EF = define_globals(FACTS_VDB)
    collections_list, collection_namelist = collection_loader(CLIENT)
    collection_name = st.selectbox('Select Collection:', 
                                   collection_namelist, 
                                   key='rm_collection_dropdown')
    # Button to delete a collection
    if st.button('Delete Collection', key='rm_collection_btn'):
        CLIENT.delete_collection(collection_name)
        st.experimental_rerun()
    pass

# Define GLOBALS ---------------------------------------------------------------
def define_globals(FACTS_VDB):
    CLIENT = chromadb.PersistentClient(path=FACTS_VDB)
    COHERE_EF = embedding_functions.CohereEmbeddingFunction(
                                    api_key="4ECOTqDXJpIYhxMQhUZxY12PPSqvgtYFclJm4Gnz", 
                                    model_name="multilingual-22-12")
    return CLIENT, COHERE_EF

def collection_loader(CLIENT):
    # Get list of collections
    collections_list = CLIENT.list_collections()
    # Get collection name from list of collections
    try:
        collection_name = CLIENT.list_collections()[0].name
    except IndexError:
        st.warning("No collection found")
    
    # Display UI ---------------------------------------------------------------
    # Display collection list
    collection_namelist = [collection.name for collection in collections_list]
    
    return collections_list, collection_namelist

def read_single_collection(CLIENT, COHERE_EF, collections_list, collection_name):
    # Get collection
    if len(collections_list) > 0 and collection_name is not None:
        query_collection = CLIENT.get_collection(name = collection_name, 
                                                embedding_function = COHERE_EF)
        # Write collection information
        st.write(query_collection)
        # Review collection documents
        len_docs = len(query_collection.get()['documents'])
        st.write(f'Number of documents: {len_docs}')
        
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
            
def title_ui(title):
    st.write(f'''<div style="text-align: center;">
                <h5 style="color: #1D5B79;
                            font-size: 40px;
                            font-weight: bold;
                ">{title}</h5>
                </div>
            ''',
                unsafe_allow_html=True)
    

    
