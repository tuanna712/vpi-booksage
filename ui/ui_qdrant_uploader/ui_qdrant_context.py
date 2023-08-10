import streamlit as st
 
from functions.qdrant_context import *
from ui.ui_qdrant_uploader.ui_ingestion import *

def ui_qdrant_context(raw_text):
    _cols = st.columns([1,9])
    with _cols[1]:
        raw_text = column_2(raw_text)
    with _cols[0]:
        column_1(raw_text)
        
def column_1(raw_text):
    if st.button('Upload', key='context_uploader'):
        with st.spinner(text='Uploading...'):
            if len(st.session_state.qdrant_url)>0 and len(st.session_state.qdrant_api_key)>0:
                qdrant_context_uploader(raw_text, st.session_state.lang)
            ingestion_context(raw_text, st.session_state.lang)
        st.success('Uploaded to QDRANT!')

def column_2(raw_text):
    st.selectbox('Select type of Defining Context:', ['Raw Text', 'Delimiter Define'], key='context_def')
    if st.session_state.context_def =='Raw Text':
        raw_text = st.text_area(label='Context', 
                            key='raw_text',
                            value=raw_text,
                            height=350,)
    if st.session_state.context_def =='Delimiter Define':
        __cols = st.columns(2)
        with __cols[0]:
            delimiter = st.text_input(label='Delimiter:', key='delimiter', value='\n\n')
            try:
                if delimiter == '\n\n':
                    splited_raw_text = raw_text.split('\n\n')
                else:
                    splited_raw_text = raw_text.split(st.session_state.delimiter)
            except ValueError:
                st.warning('Delimiter not found!')
                st.stop()
            st.write('Number of Context:', len(splited_raw_text))
        with __cols[1]:
            st.number_input(label='Number of Context:', key='n_context', 
                            min_value=0, max_value=len(splited_raw_text), value=0)
        try:
            st.text_area(label='Context',
                        key='splited_raw_text',
                        value=splited_raw_text[st.session_state.n_context],
                        height=350,)
            raw_text = splited_raw_text
        except IndexError:
            st.warning('Please check number of context!')
    return raw_text
    pass