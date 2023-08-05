import base64
import streamlit as st

from functions.ingestion import *

def ingestion_params(FACTS_VDB):
    #DataLoader--------------------------------------------
    upload_form = st.form('uploader')
    with upload_form:
        uploaded_file = file_uploader()
        _btn = upload_form.form_submit_button('Process/Create/Update')
    if uploaded_file is not None and _btn:
        with st.spinner(text='Processing...'):
            if st.session_state.book_lang == 'ENG':
                _book_lang = 'en'
            else:
                _book_lang = 'vi'
            PrivateDoc = DocProcessing(uploaded_file,
                                        chunk_size=st.session_state.chunk_size,
                                        chunk_overlap=st.session_state.chunk_overlap,
                                        collection_name=st.session_state.collection_name,
                                        book_lang=_book_lang,
                                        vector_path=FACTS_VDB,
                                        )
            PrivateDoc.file_processing()
            st.session_state.private_doc = PrivateDoc
    if 'private_doc' in st.session_state:
            _main_cols = st.columns(2)
            with _main_cols[0]:
                st.write('Chunks Histogram')
                st.session_state.private_doc.display_chunks_hist()
            with _main_cols[1]:
                n_max_chunks = st.session_state.private_doc.total_number_of_chunks()
                _num_chunk = st.number_input('Chunk Number:', min_value=1, max_value=n_max_chunks, 
                                                value=n_max_chunks, key='_num_chunk')
                chunks = st.session_state.private_doc.display_chunks(_num_chunk)
                try:
                    st.write(chunks[_num_chunk-1].page_content.replace('_', ' '))
                except AttributeError:
                    st.write(chunks[_num_chunk-1].replace('_', ' '))
                    st.info('No available metadata')
                pass
    
def file_uploader():
    sub_cols = st.columns(5)
    with sub_cols[0]:
        uploaded_file = st.file_uploader("Documents Uploader:", 
                                    type = ['pdf', 'doc', 'docx'],
                                    accept_multiple_files=False,
                                    )
    with sub_cols[1]:
        st.radio(label='Language of Document', 
                options=['ENG', 'VIE'], 
                key='book_lang',
                )
    with sub_cols[2]:
        st.number_input(label='Chunk Size', min_value=0, value=500, key='chunk_size')
    with sub_cols[3]:
        st.number_input(label='Chunk Overlap', min_value=0, value=100, key='chunk_overlap')
    with sub_cols[4]:
        st.text_input(label='Collection Name', key='collection_name')
    return uploaded_file
    
# def parameter_form():
#     parameter_form = st.form('parameters')
#     with parameter_form:
#         _btn = parameter_form.form_submit_button('Process')
    
def displayPDF(file):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # Embedding PDF in HTML, PDF file <2MB
    pdf_display =  F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>' 
    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)
    
def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://i.ibb.co/LPp2TTB/logo.png);
                background-repeat: no-repeat;
                background-size: 230px 230px;
                padding-top: 120px;
                padding-left: 10px;
                background-position: 20px 20x;
            }
            [data-testid="stSidebarNav"]::before {
                content: "VPI-Sage";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 100px;
                font: 30px sans-serif;
                color: rgb(186, 38, 15);
                text-align: center;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
def ui_sidebar_ingestion():
    with st.sidebar:
        if 'user_email' in st.session_state:
            st.write(f"User: {st.session_state.user_email}")
    pass