import docx2txt
import tiktoken
import streamlit as st
import pandas as pd
from functions.facts_gen_multi import *

def ui_multiple_questions(FACTS_DB):
    # Display title
    ui_title()
    # Define Sub-tabs
    subtab1, subtab2, subtab3, subtab4= st.tabs(['File Uploader', 'QnA Generator', 'Review', 'Qdrant Uploader'])
    
    # Upload context and questions
    with subtab1: # File Uploader and Review
        cols = st.columns(2)
        with cols[0]:
            raw_text = ui_context_uploader()
        with cols[1]:
            questions = ui_question_uploader()
    if raw_text is not None and questions is not None:
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
        with subtab3: # Review
            # Scan and select all path of .xlsx files in FACTS_DB
            files = []
            for r, d, f in os.walk(FACTS_DB):
                for file in f:
                    if '.xlsx' in file:
                        files.append(file)
            # Select file to review
            if len(files) > 0:
                file_to_review = st.selectbox('Select file to review:', files, key='file_to_review')
                # Read file
                read_df = pd.read_excel(os.path.join(FACTS_DB, file_to_review))
                # Print dataframe
                st.dataframe(read_df, height=600)
            pass
                    
        with subtab4: # Qdrant Uploader
            # Define QDRANT ID, KEY
            qdrant_id()
            if st.session_state.lang == 'Vietnamese':
                lang = 'vi'
            else:
                lang = 'en'
            if len(st.session_state.qdrant_url)>0 and len(st.session_state.qdrant_api_key)>0:
                if st.button('Upload to QDRANT'):
                    with st.spinner(text='Uploading...'):
                        qdrant_faq_uploader(FACTS_DB, lang)
                        # qdrant_context_uploader(raw_text, lang)
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
    
def multiple_questions_generator(question_df, context, FACTS_DB, question_col, ans_col, q_start, q_end):
    with st.spinner(text='Generating QnA...'):
        with st.expander("Questions and Answers", expanded=False):
            for i in range(q_start, q_end):
                question = question_df.loc[i, question_col]
                question_df.loc[i,ans_col] = responding_claude(question, context
                                                                ).replace('<tag>', ''
                                                                ).replace('</tag>', '')
                st.info(f"Question {i}: \
                        \n\nQ: {question}\
                        \n\nA: {question_df.loc[i,ans_col]}\
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