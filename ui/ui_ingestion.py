import base64
import streamlit as st

from functions import *

def tab1_main():
    #DataLoader--------------------------------------------
    uploaded_file = las_file_uploader()
    PrivateDoc = DocProcessing(uploaded_file)
    
    
def las_file_uploader():
    uploaded_file = st.file_uploader("Documents Uploader:", 
                                     type = ['pdf', 'doc', 'docx'],
                                     accept_multiple_files=False,
                                     )
    return uploaded_file
        
def displayPDF(file):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # Embedding PDF in HTML, PDF file <2MB
    pdf_display =  F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>' 
    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)
    