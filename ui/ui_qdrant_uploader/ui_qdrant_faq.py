import streamlit as st

from functions.qdrant_faq import *

def ui_qdrant_faq(FACTS_DB):
    _cols = st.columns([1,9])
    with _cols[1]:
        file_path = column_2(FACTS_DB)
    with _cols[0]:
        column_1(file_path)
        
def column_1(file_path):
    if st.button('Upload', key='faq_uploader'):
        with st.spinner(text='Uploading...'):
            if len(st.session_state.qdrant_url)>0 and len(st.session_state.qdrant_api_key)>0:
                qdrant_faq_uploader(file_path, st.session_state.lang)
            faq_collection_name = st.session_state.user + '_factsdb'
            upload_chat_faq(st.session_state.df, faq_collection_name)
        st.success('Uploaded to QDRANT!')

def column_2(FACTS_DB):
    # Check are there any .xlsx file in FACTS_DB
    files = []
    for r, d, f in os.walk(FACTS_DB):
        for file in f:
            if '.xlsx' in file:
                files.append(file)
    if len(files) > 0:
        selected_file = st.selectbox('Select file to upload:', files, key='_faq_file')
        file_path = os.path.join(FACTS_DB, selected_file)
        st.session_state.df = pd.read_excel(file_path)
        st.dataframe(st.session_state.df, height=300, width=1200)
    else:
        st.warning('No file found!')
        st.stop()
    return file_path

def qdrant_id():
    _cols = st.columns(2)
    with _cols[0]:
        st.text_input(label='QDRANT URL:', key='qdrant_url')
    with _cols[1]:
        st.text_input(label='QDRANT API KEY:', key='qdrant_api_key', type='password')
    st.radio('Language', ['Vietnamese', 'English'], key='selected_lang', horizontal=True)
    if st.session_state.selected_lang == 'Vietnamese':
        st.session_state.lang = 'vi'
    else:
        st.session_state.lang = 'en'