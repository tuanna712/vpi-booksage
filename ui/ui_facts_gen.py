import docx2txt
import tiktoken
import streamlit as st
import pandas as pd
from functions.facts_gen_multi import *
from functions.sharepoint_uploader import *
from functions.qdrant_faq import *
from functions.qdrant_context import *
from functions.data_uploader import *

from ui.ui_facts_review.ui_facts_table_review import *
from ui.ui_facts_review.ui_facts_question_review import *
from ui.ui_qdrant_uploader.ui_qdrant_faq import *
from ui.ui_qdrant_uploader.ui_qdrant_context import *
from ui.ui_qdrant_uploader.ui_ingestion import *

def ui_multiple_questions(FACTS_DB):
    # Display title
    ui_title()
    # Define Sub-tabs
    subtab1, subtab2, subtab3, subtab4= st.tabs(['File Uploader', 'QnA Generator', 'Review', 'Qdrant Uploader'])
    
    # Upload context and questions
    # ------------------------------------------------------------------------------------
    with subtab1: # File Uploader and Review
        cols = st.columns(2)
        with cols[0]:
            raw_text = ui_context_uploader()
        with cols[1]:
            questions = ui_question_uploader()
    if raw_text is not None and questions is not None:
    # ------------------------------------------------------------------------------------
        with subtab2: # QnA Generator
            subtab2_cols = st.columns(2)
            if questions is not None:
                with subtab2_cols[0]:
                # Select Question Column from Question Dataframe
                    question_col = st.selectbox('Select Question Column:', questions.columns, key='question_col')
                with subtab2_cols[1]:
                    ans_col = st.selectbox('Select Column for writing new Answer:', questions.columns, key='ans_col')
                    
            # Select range of questions
            q_range = st.form(key='range_form')
            with q_range:
                if questions is not None:
                    q_start, q_end = st.slider('Select range of questions:', 0, len(questions), (0, len(questions)))
                else:
                    q_start, q_end = 0, 0
                st.text_input(label='Set name of answered Excel output File', key='file_version')
                q_range_btn = q_range.form_submit_button(label='Start generating QnA')
        
            # Start generating QnA
            if q_range_btn:
                try:
                    multiple_questions_generator(questions, raw_text, FACTS_DB, question_col, ans_col, q_start, q_end)
                except UnboundLocalError:
                    st.warning('Please upload context, questions, choose proper columns and set range of questions first!')
                    st.stop()
                    
    # ------------------------------------------------------------------------------------
        with subtab3: # Review
            subtab31, subtab32 = st.tabs(['Table View', 'Question Review'])
            with subtab31:
                facts_table_view(FACTS_DB)
            with subtab32:
                facts_question_view(FACTS_DB)
                             
    # ------------------------------------------------------------------------------------
        with subtab4: # Qdrant Uploader
            # Define QDRANT_ID, API_KEY
            qdrant_id()
            # Define Context VectorDB, FAQ VectorDB tabs
            subtab41, subtab42 = st.tabs(['Context VectorDB', 'FAQ VectorDB'])
            # With Context VectorDB Tab
            with subtab41:
                ui_qdrant_context(raw_text)
            # With FAQ VectorDB Tab
            with subtab42:
                ui_qdrant_faq(FACTS_DB)
    
def multiple_questions_generator(question_df, context, FACTS_DB, question_col, ans_col, q_start, q_end):
    my_bar = st.progress(0, text='Answers Generating...')
    with st.spinner(text='Generating Answers...'):
        with st.expander("Questions and Answers", expanded=False):
            for percent_complete in range(q_end - q_start):
                for i in range(q_start, q_end):
                    question = question_df.loc[i, question_col]
                    question_df.loc[i,ans_col] = responding_claude(question, context
                                                                    ).replace('<tag>', ''
                                                                    ).replace('</tag>', '')
                    st.info(f"Question {i}: \
                            \n\nQ: {question}\
                            \n\nA: {question_df.loc[i,ans_col]}\
                            ")
                    question_df.to_excel(f'{FACTS_DB}/{st.session_state.file_version}.xlsx', index=False)
        my_bar.progress(percent_complete + 1)
    
    DatabaseLink(st.session_state.user_email).upload_overwrite()
    st.success('Generated all QnAs!')
    
    pass
    
def ui_title():
    st.write(f'''<div style="text-align: center;">
                <h5 style="color: #1D5B79;
                            font-size: 40px; 
                            font-weight: bold;
                ">
                Multiple Questions Generator</h5>
                </div>
            ''',
                unsafe_allow_html=True)