import docx2txt
import tiktoken
import streamlit as st
import pandas as pd
from functions.facts_gen_multi import *

def ui_multiple_questions(FACTS_DB):
    # Display title
    ui_title()
    # Define Sub-tabs
    subtab1, subtab2, subtab3 = st.tabs(['File Uploader and Review', 'QnA Generator', 'Qdrant Uploader'])
    
    # Upload context and questions
    with subtab1:
        cols = st.columns(2)
        with cols[0]:
            raw_text = ui_context_uploader()
        with cols[1]:
            questions = ui_question_uploader()
    with subtab2:
        if st.button('Start'):
            multiple_questions_generator(questions, raw_text, FACTS_DB) 
            
    with subtab3:
        # Define QDRANT ID, KEY
        qdrant_id()
        if st.session_state.lang == 'Vietnamese':
            lang = 'vi'
        else:
            lang = 'en'
        if st.session_state.qdrant_url is not None and st.session_state.qdrant_api_key is not None:
            if st.button('Upload to QDRANT'):
                with st.spinner(text='Uploading...'):
                    qdrant_faq_uploader(FACTS_DB, lang)
                    qdrant_context_uploader(raw_text, lang)
            st.success('Uploaded to QDRANT!')
        else:
            st.warning('QDRANT ID and API KEY should not be empty!!!')
def qdrant_id():
    _cols = st.columns(2)
    with _cols[0]:
        st.text_input(label='QDRANT URL:', key='qdrant_url')
    with _cols[1]:
        st.text_input(label='QDRANT API KEY:', key='qdrant_api_key', type='password')
    st.radio('Language', ['Vietnamese', 'English'], key='lang')
def ui_context_uploader():
    raw_text = None
    context_file = st.file_uploader("Upload context file", type=["txt", "docx", "doc"], 
                                    key='context_file_uploader')
    if context_file is not None and context_file.name.endswith('.txt'):
        raw_text = context_file.getvalue().decode('utf-8')

    if context_file is not None and [context_file.name.endswith('.docx') or 
                                     context_file.name.endswith('.doc')]:
    # Read docx/doc file
        if context_file.type == 'text/plain':
            raw_text = str(context_file.read(),"utf-8") 
        # elif context_file.type == "application/pdf":
            # raw_text = read_pdf(context_file)
        elif context_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            raw_text = docx2txt.process(context_file)
        elif context_file.type == "application/msword":
            raw_text = docx2txt.process(context_file)
    if raw_text is not None:
        tokenizer = tiktoken.get_encoding('cl100k_base')
        tokens = tokenizer.encode(raw_text, disallowed_special=())
        if len(tokens) > 60000:
            st.warning(f"Tokens: {len(tokens)}. Context is too long. \
                Please upload a shorter context.\
                Length of context should be less than 60.000 tokens (45.000 words).")
        else:
            st.info(f"Context uploaded! Tokens: {len(tokens)}. ")
        with st.expander("Context", expanded=False):
            st.write(raw_text)
        return raw_text
            
def ui_question_uploader():
    question_file = st.file_uploader("Upload question file", type=["xlsx"], key='question_file_uploader')
    if question_file is not None:
        questions = pd.read_excel(question_file)
        with st.expander("Questions", expanded=False):
            # Print dataframe
            st.dataframe(questions)
        return questions
    
def multiple_questions_generator(question_df, context, FACTS_DB):
    with st.spinner(text='Generating QnA...'):
        with st.expander("Questions and Answers", expanded=False):
            for i in range(len(question_df)):
                question = question_df.loc[i,'Câu hỏi?']
                question_df.loc[i,'Trả lời'] = responding_claude(question, context
                                                                ).replace('<tag>', ''
                                                                ).replace('</tag>', '')
                st.info(f"Question {i}: \
                        \n\nQ: {question}\
                        \n\nA: {question_df.loc[i,'Trả lời']}\
                        ")
                question_df.to_excel(f'{FACTS_DB}/multiple_questions_gen.xlsx', index=False)
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