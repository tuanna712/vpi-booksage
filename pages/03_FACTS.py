import json
import pandas as pd
import streamlit as st
from ui import *
from functions import *
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
    with st.sidebar:
        fact_ui_options = st.radio('Facts UI', ['Generater', 'Review', 'Edit'], key='fact_ui_options')

    if fact_ui_options == 'Generater':
        ui_facts_gen()
    if fact_ui_options == 'Review':
        read_df = read_fact_db()
        display_single_fact(read_df)
    if fact_ui_options == 'Edit':
        read_df = read_fact_db()
        edit_fact_db(read_df)
        pass

# --- UI 4 GEN ------------------------------------------------------------------------
def ui_facts_gen():
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
        # Action button for Facts Analysis -> CALL QnA Generater
        fact_form_btn = fact_form.form_submit_button(label='Generate QnA')
    #  --- GENERATE QnA ---------------------------------------------------------------
    if fact_form_btn:
        with st.spinner(text='Generating QnA...'):
            try:
                # Take QnA Action
                _question, _answer = qna_generater_openai(facts_input)
            except ValueError:
                st.write("Can't detect structure of LLM output . Please try again.")
    # --- EDIT QnA --------------------------------------------------------------------
    if '_question' in st.session_state:
        with editable_form:
            qna_display(st.session_state._question, st.session_state._answer)
            editable_form_btn = editable_form.form_submit_button(label='Save')
        
    # --- Save Facts -----------------------------------------------------------------
        if editable_form_btn:
            save_qadb(st.session_state._llm_qst, st.session_state.llm_ans, st.session_state.facts_input)

def qna_display(_question, _answer):
    col1, col2 = st.columns([1,2])
    # Question edit
    with col1:
        edited_llm_qst = st.text_area('QstGenerater:', _question, height=200, key="_llm_qst")
    # Answer edit
    with col2:
        edited_llm_ans = st.text_area('AnsGenerater:', _answer, height=200, key="llm_ans")
    
def qna_generater_openai(context:str):
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
    
def save_qadb(_question:str, _answer:str, context:str):
    # Check if /qadb/qadb.json is file
    qadb_path = 'qadb/qadb.json'
    if os.path.isfile(qadb_path):
        df = pd.read_json('qadb/qadb.json')
    else:
        # Create a new pd df
        df = pd.DataFrame(columns=['question', 'answer', 'context'])

    # Define new QA row
    new_row = {"question": _question, "answer": _answer, 'context': context}
    new_df = pd.DataFrame([new_row])
    # Update df
    df = pd.concat([df, new_df], ignore_index=True)
    # ---------------------------------------------
    # Save df to json
    df = df.drop_duplicates()
    df.to_json('qadb/qadb.json')
    # ---------------------------------------------
    print("Saved to qadb/qadb.json")
    st.success("Saved to database")
    
def read_fact_db():
    #check if /qadb/qadb.json is file
    qadb_path = 'qadb/qadb.json'
    if os.path.isfile(qadb_path):
        #load qadb.json file as a pandas df
        read_df = pd.read_json('qadb/qadb.json')
        return read_df
    else:
        st.info("No facts database found")
        pass
def display_single_fact(df):
    n_facts = len(df)
    for i in range(n_facts):
        _q = df.iloc[i]['question']
        _a = df.iloc[i]['answer']
        _c = df.iloc[i]['context']
        st.write(f'''<div style="text-align: center;">
                    <h5 style="color: #1D5B79;
                                font-size: 20px; 
                                font-weight: bold;
                    ">
                    Fact number: {i+1}</h5>
                    </div>
                ''',
                    unsafe_allow_html=True)
        # st.warning(f"Question number: {i+1}")
        st.info(f"Context: {_c}")
        st.warning(f"Question: {_q}")
        st.success(f"Answer: {_a}")
    pass
def edit_fact_db(df):
    st.write(f'''<div style="text-align: center;">
                    <h5 style="color: #1D5B79;
                                font-size: 40px; 
                                font-weight: bold;
                    ">
                    Facts Editing</h5>
                    </div>
                ''',
                    unsafe_allow_html=True)
    fact_num_form = st.form(key='fact_num_form')
    # FACT NUMBER FORM
    with fact_num_form:
        e_n_fact = st.number_input('Enter fact number you want to edit', 
                                min_value=1, max_value=len(df),
                                value=1, step=1,
                                key='e_n_fact')
        show_fact_btn = fact_num_form.form_submit_button('Show')
    # FACT FORM ACTION
    if show_fact_btn or 'e_n_fact' in st.session_state:
        show_editing_fact(df, e_n_fact)
        # SAVE AND DELETE BUTTONs
        _sub_cols = st.columns([1,1,1,1,1])
        with _sub_cols[1]:
            save_fact_btn = st.button('Save', key='save_fact_btn')
        with _sub_cols[3]:
            delete_fact_btn = st.button('Delete', key='delete_fact_btn')
        if save_fact_btn:
            try:
                save_editing_fact(df, e_n_fact)
            except AttributeError:
                st.warning('You have not edited anything yet')
        if delete_fact_btn:
            delete_editing_fact(df, e_n_fact)

def show_editing_fact(df, e_n_fact):
    st.session_state.recall_context_by_id = df.loc[e_n_fact-1,'context']
    st.session_state.recall_question_by_id = df.loc[e_n_fact-1,'question']
    st.session_state.recall_answer_by_id = df.loc[e_n_fact-1,'answer']
    # Display editing fact
    st.text_area('Context:', st.session_state.recall_context_by_id, height=200, key="e_ct_db")
    # Layout for question and answer
    col1, col2 = st.columns([1,2])
    with col1:
        # Question edit
        st.text_area('Question:', st.session_state.recall_question_by_id, height=200, key="e_qst_db")
    with col2:
        # Answer edit
        st.text_area('Answer:', st.session_state.recall_answer_by_id, height=200, key="e_ans_db")

def save_editing_fact(df, e_n_fact):
    if 'e_ct_db' in st.session_state:
        df.loc[e_n_fact-1,'context'] = st.session_state.e_ct_db
        st.success('Context saved')
    if 'e_qst_db' in st.session_state:
        df.loc[e_n_fact-1,'question'] = st.session_state.e_qst_db
        st.success('Updated Question')
    if 'e_ans_db' in st.session_state:
        df.loc[e_n_fact-1,'answer'] = st.session_state.e_ans_db
        st.success('Updated Answer')
    # Save to json file
    df.to_json('qadb/qadb.json')
    st.success('Saved to database')
        
def delete_editing_fact(df, e_n_fact):
    df = df.drop([e_n_fact-1]).reset_index(drop=True)
    df.to_json('qadb/qadb.json')
    st.warning('The fact has been deleted and the fact order has been updated')
    
    pass
#CHATPGT-RESPONSES-----------------------------------------------------------
def responding_openai(prompt):
    import openai; openai.api_key = os.getenv('OPENAI_API_KEY')
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
        
    \nHuman: 'The structural pattern of Vietnam and its adjacent areas is dominated by two major\
            fault systems: the NW-SE and NE-SW trending faults, co-existing with two other less dominant N-S and E-W trending systems.\
            Even though the latter two are less developed and not as widespread, they also play an important role in the petroleum system of the region.'
    
    \nAI: 'What are the two major fault systems of Vietnam and its adjacent areas? ----- The geological structure of Vietnam and surrounding areas\
            is shaped primarily by two major fault systems running northwest-southeast and northeast-southwest. Additionally, two less dominant \
            fault systems trending north-south and east-west exist in the region. While not as extensive, these minor systems also contribute \
            significantly to the oil and gas systems in the area.'\
                
    \nHuman: 'Vietnam lies between 8 o 30 N - 23 o 02 N, stretching from Lung Cu village (Dong Van district, Ha Giang province) \
    in the North to Mui hamlet (Nam Can district, Ca Mau province) in the South. The length of the country is about four times\
    that of its width. Its widest point is around 500 km (Mong Cai, Quang Ninh - Dien Bien) while the narrowest point is only \
    50 km wide (the frontier of Viet - Laos to Dong Hoi, Quang Binh province) (Fig. 1.1 and 1.2). Vietnam’s mainland covers 329,229 km2.'

    \nAI: 'What is the geographical span of Vietnam? ----- The approximate width of Vietnam at its narrowest point is 50 km \
        (from the frontier of Viet-Laos to Dong Hoi, Quang Binh province), while its widest point is around 500 km \
        (from Mong Cai, Quang Ninh to Dien Bien).'\
    
    \nHuman: {facts}
    
    \nAI:
    """
    return _prompt
# context = "Outside its mainland territory, Vietnam has a continental shelf, and thousands of islands and archipelagoes such as those in the Gulf of Bac Bo (before named the gulf of Tonkin), the Hoang Sa (Paracel) and Truong Sa (Spratly) Archipelagoes in the East Sea, and the Tho Chu, Phu Quoc islands in the Gulf of Thailand. Two thirds of Vietnam’s territory is covered with hills and mountains. The most mountainous area belongs to the northwest, from the upper reaches of Ma River to the Red river valley. The Fansipan summit, at 3,148m, is the highest peak in the Indochina. The Viet Bac Mountains, located on Chay River’s right bank and terminated at the Red river valley, are made up of such peaks as Tay Con Linh (2,431 m high), and Kieu Lieu Ti (2,402 m). The northeastern hills-mountains, spreading from Lo river valley to coastal area of Quang Ninh province, are bow-shaped ranges protruding to the sea (Gam River, Yen Lac, Bac Son, and Dong Trieu bows). The Truong Son mountain range, exten-ding from the southern part of Xieng Khoang plateau (Laos) to the southern part of Central Vietnam, consists of Pu Lai Leng peak (2,711m), Rao Co (2,335 m), and Ngoc Linh, Ngoc Niay, Ngoc Pan, Ngoc Kring peaks; The Lam Vien, Bao Loc, and Di Linh and Mnong plateaus shape a plateau massif at the southern tip of Vietnam."
main()