import base64, os
import pdfplumber
import streamlit as st
from docx import Document

def file_loading(uploaded_file):
    if uploaded_file is not None:
            #Split file extension for detection of loading type
            file_extension = os.path.splitext(uploaded_file.name)[-1]
            #Load PDF file
            if file_extension == ".pdf":
                doc = pdfplumber.open(uploaded_file)
                st.write(doc.pages[0].extract_text())
                print('Loaded PDF file!\n')
            #Load MS Word file
            if file_extension in [".doc", ".docx"]:
                doc = Document(uploaded_file)
                paragraphs = [p.text for p in doc.paragraphs]
                st.header("Word File Content:")
                for paragraph in paragraphs:
                    st.write(paragraph)
                print('Loaded MS Word file!\n')
            return doc