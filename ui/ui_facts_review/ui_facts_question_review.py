import os
import streamlit as st
import pandas as pd
from functions.excel_downloader import *

def facts_question_view(FACTS_DB):
    # Scan and select all path of .xlsx files in FACTS_DB
    files = []
    for r, d, f in os.walk(FACTS_DB):
        for file in f:
            if '.xlsx' in file:
                files.append(file)
    _cols = st.columns(2)
    # Select file to review
    if len(files) > 0:
        with _cols[0]:
            file_to_review = st.selectbox('Select file to review:', files, key='single_question_review')
            file_path = os.path.join(FACTS_DB, file_to_review)
        read_df = pd.read_excel(file_path)
    if 'single_question_review' in st.session_state and st.session_state.single_question_review is not None:
        with _cols[1]:
            n_q = st.number_input(label='Question number:', 
                            min_value=0, max_value=len(read_df), 
                            key='question_number')
        edit_form = st.form(key='edit_form')
        with edit_form:
            st.text_area(label=f'Question {n_q}:', 
                         value=read_df['Câu hỏi'][n_q], 
                         key='question',
                         height=100,
                         )
            st.text_area(label='Answer:', 
                         value=read_df['Trả lời'][n_q], 
                         key='answer',
                         height=400,
                         )
        edit_form_submit = edit_form.form_submit_button(label='Save')
        if edit_form_submit:
            # Save to dataframe
            read_df['Câu hỏi'][n_q] = st.session_state.question
            read_df['Trả lời'][n_q] = st.session_state.answer
            # Save to local
            read_df.to_excel(file_path, index=False)
            print(f'Saved question {n_q} to file {file_path}')
            # Sync to SharePoint
            upload_single_file(file_path)
            print(f'Synced question {n_q} to SharePoint')
            st.success(f'Saved and synchronized!')
        
        # Download Excel file
        df_xlsx = to_excel(read_df)
        st.download_button(label='📥 Download Excel',
                                        data=df_xlsx ,
                                        file_name= 'FAQs.xlsx')
    
def upload_single_file(_path):
    from office365.sharepoint.client_context import ClientContext
    from office365.runtime.auth.client_credential import ClientCredential
    from dotenv import load_dotenv
    load_dotenv()
    local_path = os.getcwd() + '/data/' + st.session_state.user
    user_url = os.environ['SHAREPOINT_PARENT_URL'] + st.session_state.user
    ctx = ClientContext(os.environ['SHAREPOINT_SITE']
                        ).with_credentials(ClientCredential(os.environ['SHAREPOINT_CLIENT_ID'], 
                                                            os.environ['SHAREPOINT_CLIENT_SECRET']
                                                            )
                                           )
    _target_site = os.path.dirname(_path.replace(local_path, user_url))
    _target_folder = ctx.web.get_folder_by_server_relative_url(_target_site)
    with open(_path, 'rb') as f:
        _target_folder.files.upload(file_name=os.path.basename(_path), content=f).execute_query()