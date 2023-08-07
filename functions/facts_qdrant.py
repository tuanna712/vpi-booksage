import os
import pandas as pd
import streamlit as st

from dotenv import load_dotenv
load_dotenv()

import cohere
from qdrant_client import QdrantClient

from langchain.schema import Document
from langchain.vectorstores import Qdrant
from langchain.embeddings import CohereEmbeddings

# Display single Fact----------------------------------------------------------
def display_single_fact(df):
    try:
        n_facts = len(df)
    except TypeError:
        st.warning("No facts database found, create new at 'Generator' tab")
        st.stop()
    values = st.slider(
                    label='Select a range of facts',
                    min_value=1, 
                    max_value=n_facts, 
                    value=(1, 3),
                    step=1,
                    key='fact_range'
                    )
    
    for i in range(values[0]-1, values[1]):
        _q = df.iloc[i]['question']
        _a = df.iloc[i]['answer']
        _c = df.iloc[i]['context']
        st.write(f'''<div style="text-align: center;">
                    <h5 style="color: #1D5B79;
                                font-size: 20px; 
                                font-weight: bold;
                    ">
                    Fact number: {i+1}</h5>
                    </div>
                ''',
                    unsafe_allow_html=True)
        # st.warning(f"Question number: {i+1}")
        st.info(f"Context: {_c}")
        st.warning(f"Question: {_q}")
        st.success(f"Answer: {_a}")

# Show Editting Fact-----------------------------------------------------------
def show_editing_fact(df, e_n_fact):
    st.session_state.recall_context_by_id = df.loc[e_n_fact-1,'context']
    st.session_state.recall_question_by_id = df.loc[e_n_fact-1,'question']
    st.session_state.recall_answer_by_id = df.loc[e_n_fact-1,'answer']
    # Display editing fact
    st.text_area('Context:', st.session_state.recall_context_by_id, height=200, key="e_ct_db")
    # Layout for question and answer
    col1, col2 = st.columns([1,2])
    with col1:
        # Question edit
        st.text_area('Question:', st.session_state.recall_question_by_id, height=200, key="e_qst_db")
    with col2:
        # Answer edit
        st.text_area('Answer:', st.session_state.recall_answer_by_id, height=200, key="e_ans_db")
# Save Edited Fact-----------------------------------------------------------
def save_editing_fact(df, e_n_fact, FACTS_JSON):
    if 'e_ct_db' in st.session_state:
        df.loc[e_n_fact-1,'context'] = st.session_state.e_ct_db
        st.success('Context saved')
    if 'e_qst_db' in st.session_state:
        df.loc[e_n_fact-1,'question'] = st.session_state.e_qst_db
        st.success('Updated Question')
    if 'e_ans_db' in st.session_state:
        df.loc[e_n_fact-1,'answer'] = st.session_state.e_ans_db
        st.success('Updated Answer')
    # Save to json file
    df.to_json(FACTS_JSON)
    st.success('Saved to database')
        
# Remove Fact-----------------------------------------------------------
def delete_editing_fact(df, e_n_fact,FACTS_JSON):
    df = df.drop([e_n_fact-1]).reset_index(drop=True)
    df.to_json(FACTS_JSON)
    st.warning('The fact has been deleted and the fact order has been updated')

# Read Facts DB-----------------------------------------------------------
def read_fact_db(FACTS_JSON):
    #check if /qadb/qadb.json is file
    qadb_path = FACTS_JSON
    if os.path.isfile(qadb_path):
        #load qadb.json file as a pandas df
        read_df = pd.read_json(qadb_path)
        return read_df
    else:
        st.info("No facts database found")
        
# Edit Facts DB-----------------------------------------------------------
def edit_fact_db(df, FACTS_JSON):
    try:
        check_df = len(df)
    except TypeError:
        st.info("No facts database found")
        st.stop()
        
    st.write(f'''<div style="text-align: center;">
                    <h5 style="color: #1D5B79;
                                font-size: 40px; 
                                font-weight: bold;
                    ">
                    Facts Editing</h5>
                    </div>
                ''',
                    unsafe_allow_html=True)
    fact_num_form = st.form(key='fact_num_form')
    # FACT NUMBER FORM
    with fact_num_form:
        e_n_fact = st.number_input('Enter fact number you want to edit', 
                                min_value=1, max_value=len(df),
                                value=1, step=1,
                                key='e_n_fact')
        show_fact_btn = fact_num_form.form_submit_button('Show')
    # FACT FORM ACTION
    if show_fact_btn or 'e_n_fact' in st.session_state:
        show_editing_fact(df, e_n_fact)
        # SAVE AND DELETE BUTTONs
        _sub_cols = st.columns([1,1,1,1,1])
        with _sub_cols[1]:
            save_fact_btn = st.button('Save', key='save_fact_btn')
        with _sub_cols[3]:
            delete_fact_btn = st.button('Delete', key='delete_fact_btn')
        if save_fact_btn:
            try:
                save_editing_fact(df, e_n_fact, FACTS_JSON)
            except AttributeError:
                st.warning('You have not edited anything yet')
        if delete_fact_btn:
            delete_editing_fact(df, e_n_fact, FACTS_JSON)
    
# Save Facts DB -----------------------------------------------------------------
def save_qadb(_question:str, _answer:str, context:str, qadb_path:str):
    # Check if qadb_path is file
    if os.path.isfile(qadb_path):
        df = pd.read_json(qadb_path)
    else:
        # Create a new pd df
        df = pd.DataFrame(columns=['question', 'answer', 'context'])

    # Define new QA row
    new_row = {"question": _question, "answer": _answer, 'context': context}
    new_df = pd.DataFrame([new_row])
    # Update df
    df = pd.concat([df, new_df], ignore_index=True)
    # ---------------------------------------------
    # Save df to json
    df = df.drop_duplicates()
    df.to_json(qadb_path)
    # ---------------------------------------------
    st.success("Saved to database")
    
# Facts VectorDB-----------------------------------------------------------
def facts_to_vectordb(FACTS_DB, FACTS_JSON):
    question_list:list = None
    # Display title
    st.write(f'''<div style="text-align: center;">
                <h5 style="color: #1D5B79;
                            font-size: 40px; 
                            font-weight: bold;
                ">
                Facts Vector Database</h5>
                </div>
            ''',
                unsafe_allow_html=True)
    # Define facts vector db path
    facts_vdb_path = FACTS_DB
    # Check if text db existed
    qadb_path = FACTS_JSON
    # Action for loading facts db
    if os.path.isfile(qadb_path):
        df = pd.read_json(qadb_path)
        # Display facts db
        st.dataframe(df, height=500, use_container_width=True )
    else:
        st.warning("No facts database found")
        
    # ---------------------------------------------
    # Load facts db Button
    st.button('Create/Update Facts DB', key='create_facts_db')
    # Create facts vector db
    # Define Qdrant endpoint and Cohere Embedding
    embeddings = CohereEmbeddings(model="multilingual-22-12", 
                                cohere_api_key=os.environ['COHERE_API_KEY'])
    qdrant_url = os.environ['QDRANT_URL']
    qdrant_api_key = os.environ['QDRANT_API_KEY']
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    if 'user_email' in st.session_state:
        collection_name = st.session_state.user_email.split('@')[0] + '_factsdb'
    else:
        st.warning('Please login first!!!')
        st.stop()
    # Action for embedding facts
    if st.session_state.create_facts_db:
        with st.spinner('Processing...'):
            # Preparing Documents before upload to Qdrant
            question_list = df['question'].tolist()
            answer_list = df['answer'].tolist()
            ids = df.reset_index(drop=True).index.tolist()
            chunks = []
            for i in range(len(question_list)):
                chunk = Document(page_content=question_list[i], 
                                    metadata={'answer': answer_list[i], 
                                            'type': 'FAQ'})
                chunks.append(chunk)
            
            # Upload and overwrite docs to Qdrant using Langchain Qdrant
            client.delete_collection(collection_name=collection_name)
            vdatabase = Qdrant.from_documents(documents=chunks,
                                            ids=ids,
                                            embedding=embeddings, 
                                            url=qdrant_url, 
                                            prefer_grpc=True, 
                                            api_key=qdrant_api_key, 
                                            collection_name=collection_name,
                                            )
        st.success("Facts vector database created/updated")
    # ---------------------------------------------
    # Input question from user
    st.text_input('Enter your question', key='input_question')
    # Load facts db Button
    st.button('Search', key='search_facts')
    # Action for embedding facts
    if st.session_state.search_facts:
        with st.spinner('Searching...'):
            cohere_client = cohere.Client(api_key=os.environ['COHERE_API_KEY'])
            results = client.search(collection_name=collection_name,
                query_vector=cohere_client.embed(texts=[st.session_state.input_question],
                                                model='multilingual-22-12',
                                                ).embeddings[0],
                limit=3
                )

        st.info(f"Top 3 relevant questions are: \n\
                \n 01. Score: {round(results[0].score, 2)} \
                    \nQuestion: {results[0].payload['page_content']}\
                    \nAnswer: {results[0].payload['metadata']['answer']}\
                \n 02. Score: {round(results[1].score, 2)}\
                    \nQuestion: {results[1].payload['page_content']}\
                    \nAnswer: {results[1].payload['metadata']['answer']}\
                \n 03. Score: {round(results[2].score, 2)}\
                    \nQuestion: {results[2].payload['page_content']}\
                    \nAnswer: {results[2].payload['metadata']['answer']}\
                    ")