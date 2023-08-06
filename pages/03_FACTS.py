import json
import pandas as pd
import streamlit as st
from functions.facts_qdrant import *
from PIL import Image

logo = Image.open("./assets/images/logo.png")
st.set_page_config(# Alternate names: setup_page, page, layout
                layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
                initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
                page_title="VPI Sage",  # String or None. Strings get appended with "• Streamlit". 
                page_icon=logo,  # String, anything supported by st.image, or None.
                )
# add_logo()
# --- LOAD CSS ------------------------------------------------------------------------
with open("./style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
# Sidebar UI --------------------------------------------------------------------------
def main():
    # Display sidebar information
    with st.sidebar:
        # Check if user is logged in---------------------------
        if 'user_email' in st.session_state:
            st.write(f"User: {st.session_state.user_email}")
            USER = st.session_state.user_email.split('@')[0]
            FACTS_JSON = f'database/{USER}/facts_db/txt_db/qadb.json'
            FACTS_DB = f'database/{USER}/facts_db/facts_vector_db'
        else:
            st.warning("Please login first")
            st.stop()
            
        # --- TABS Definition ---------------------------------
        fact_ui_options = st.radio('Facts UI', ['Generator', 'Review', 'Edit', 'Database'], 
                                   key='fact_ui_options')
    # --- UI Generator ----------------------------------------
    if fact_ui_options == 'Generator':
        ui_facts_gen(FACTS_JSON)
    # --- UI Review -------------------------------------------
    if fact_ui_options == 'Review':
        read_df = read_fact_db(FACTS_JSON)
        display_single_fact(read_df)
    # --- UI Edit ---------------------------------------------
    if fact_ui_options == 'Edit':
        read_df = read_fact_db(FACTS_JSON)
        edit_fact_db(read_df, FACTS_JSON)
    # --- UI Database -----------------------------------------
    if fact_ui_options == 'Database':
        facts_to_vectordb(FACTS_DB, FACTS_JSON)

# --- UI 4 GEN ------------------------------------------------------------------------
def ui_facts_gen(FACTS_JSON):
    fact_form = st.form(key='fact_form')
    editable_form = st.form(key='editable_form')
    with fact_form:
        # Check if facts input existed then assign to _value
        if 'facts_input' in st.session_state:
            _value = st.session_state.facts_input
        else:
            _value = ""
        # Display facts input text area
        facts_input = st.text_area('Facts Analysis:',value=_value, height=200, key="facts_input")
        # Action button for Facts Analysis -> CALL QnA Generator
        fact_form_btn = fact_form.form_submit_button(label='Generate QnA')
    #  --- GENERATE QnA ---------------------------------------------------------------
    if fact_form_btn:
        with st.spinner(text='Generating QnA...'):
            try:
                # Take QnA Action
                _question, _answer = qna_generator_openai(facts_input)
            except ValueError:
                st.write("Can't detect structure of LLM output . Please try again.")
    # --- EDIT QnA --------------------------------------------------------------------
    if '_question' in st.session_state:
        with editable_form:
            qna_display(st.session_state._question, st.session_state._answer)
            editable_form_btn = editable_form.form_submit_button(label='Save')
        
    # --- Save Facts -----------------------------------------------------------------
        if editable_form_btn:
            save_qadb(st.session_state._llm_qst, 
                      st.session_state.llm_ans, 
                      st.session_state.facts_input,
                      FACTS_JSON,)

# QnA Displaying -----------------------------------------------------------------
def qna_display(_question, _answer):
    col1, col2 = st.columns([1,2])
    # Question edit
    with col1:
        edited_llm_qst = st.text_area('QstGenerator:', _question, height=200, key="_llm_qst")
    # Answer edit
    with col2:
        edited_llm_ans = st.text_area('AnsGenerator:', _answer, height=200, key="llm_ans")
    
# QnA Generator -----------------------------------------------------------------
def qna_generator_openai(context:str):
    facts = context
    # Prompting
    prompt = prompting(facts)
    # Call OpenAI
    results = responding_openai(prompt)
    # Split results into question and answer
    _question, _answer = results.split('-----')
    # Save to session state
    st.session_state._question = _question
    st.session_state._answer = _answer
    # Display QnA
    return _question, _answer
    
#CHATPGT-RESPONSES-----------------------------------------------------------
def responding_openai(prompt):
    import openai
    openai.api_key = os.getenv('OPENAI_API_KEY')
    response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-16k",
                    messages=[{"role": "system", "content": "You act as a self question-answer master that gives a \
                        comprehensive simple pair of questions and answer based on the given context. \
                        By your experience, please provide me with a question that resembles a general or summary question.\
                        The final response follows this structure: question ----- answer. There are some examples below for your reference."},
                            {"role": "user", "content": prompt}],
                    max_tokens = 2000,
                    n=1,
                    temperature=0.1,
                    top_p=1,
                )
    results = response.choices[0].message.content
    chatgpt_tokens = response.usage.total_tokens
    return results

def prompting(facts):
    _prompt = f"""
    You act as a self question-answer master that gives a comprehensive simple pair of questions and answer based on the given context. \
    By your experience, please provide me with a question that resembles a general or summary question.\
    The final response follows this structure: question ----- answer. There are some examples below for your reference.\
        
    \nHuman: The structural pattern of Vietnam and its adjacent areas is dominated by two major\
            fault systems: the NW-SE and NE-SW trending faults, co-existing with two other less dominant N-S and E-W trending systems.\
            Even though the latter two are less developed and not as widespread, they also play an important role in the petroleum system of the region.
    
    \nAI: What are the two major fault systems of Vietnam and its adjacent areas? ----- The geological structure of Vietnam and surrounding areas\
            is shaped primarily by two major fault systems running northwest-southeast and northeast-southwest. Additionally, two less dominant \
            fault systems trending north-south and east-west exist in the region. While not as extensive, these minor systems also contribute \
            significantly to the oil and gas systems in the area.\
                
    \nHuman: Vietnam lies between 8 o 30 N - 23 o 02 N, stretching from Lung Cu village (Dong Van district, Ha Giang province) \
    in the North to Mui hamlet (Nam Can district, Ca Mau province) in the South. The length of the country is about four times\
    that of its width. Its widest point is around 500 km (Mong Cai, Quang Ninh - Dien Bien) while the narrowest point is only \
    50 km wide (the frontier of Viet - Laos to Dong Hoi, Quang Binh province) (Fig. 1.1 and 1.2). Vietnam’s mainland covers 329,229 km2.

    \nAI: What is the geographical span of Vietnam? ----- The approximate width of Vietnam at its narrowest point is 50 km \
        (from the frontier of Viet-Laos to Dong Hoi, Quang Binh province), while its widest point is around 500 km \
        (from Mong Cai, Quang Ninh to Dien Bien).\
    
    \nHuman: {facts}
    
    \nAI:
    """
    return _prompt

main()