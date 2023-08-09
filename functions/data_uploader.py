import docx2txt
import tiktoken
import streamlit as st
import pandas as pd

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