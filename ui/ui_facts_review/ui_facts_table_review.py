import os
import streamlit as st
import pandas as pd

def facts_table_view(FACTS_DB):
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