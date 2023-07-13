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
                page_title="BookSage",  # String or None. Strings get appended with "• Streamlit". 
                page_icon=logo,  # String, anything supported by st.image, or None.
                )
# add_logo()
# --- LOAD CSS ------------------------------------------------------------------------
with open("./style/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
# Sidebar UI --------------------------------------------------------------------------
def main():
    with st.sidebar:
        fact_ui_options = st.radio('Facts UI', ['Generater', 'Review'], key='fact_ui_options')

    if fact_ui_options == 'Generater':
        # --- FACTs TO QnA --------------------------------------------------------------------
        ui_facts_gen()
    if fact_ui_options == 'Review':
        st.header("Facts Review")
        read_fact_db()
        pass

# --- UI 4 GEN ------------------------------------------------------------------------
def ui_facts_gen():
    fact_form = st.form(key='fact_form')
    editable_form = st.form(key='editable_form')
    with fact_form:
        facts_input = st.text_area('Facts Analysis:', height=200, key="facts_input")
        fact_form_btn = fact_form.form_submit_button(label='Generate QnA')
    #  --- GENERATE QnA ---------------------------------------------------------------
    if fact_form_btn:
        _question, _answer = qna_generater(facts_input)
        st.session_state._question, st.session_state._answer = _question, _answer
    # --- EDIT QnA --------------------------------------------------------------------
    if '_question' in st.session_state:
        with editable_form:
            qna_display(st.session_state._question, st.session_state._answer)
            editable_form_btn = editable_form.form_submit_button(label='Save')
        
    # --- Save Facts -----------------------------------------------------------------
        if editable_form_btn:
            save_qadb(st.session_state.llm_qst, st.session_state.llm_ans)

def qna_display(_question, _answer):
    col1, col2 = st.columns([1,2])
    # Question edit
    with col1:
        edited_llm_qst = st.text_area('QstGenerater:', _question, height=200, key="llm_qst")
    # Answer edit
    with col2:
        edited_llm_ans = st.text_area('AnsGenerater:', _answer, height=200, key="llm_ans")
    
def qna_generater(context:str, QA_db:dict=None):
    import openai, os, json
    openai.api_key = os.getenv('OPENAI_API_KEY')
    from langchain.chat_models import ChatOpenAI
    from langchain import PromptTemplate, LLMChain
    from langchain.prompts.chat import (
        ChatPromptTemplate,
        SystemMessagePromptTemplate,
        AIMessagePromptTemplate,
        HumanMessagePromptTemplate,
    )
    from langchain.schema import AIMessage, HumanMessage, SystemMessage
    # create a chat model
    chat = ChatOpenAI(temperature=0)
    # create a prompt template
    template = "You are a questioner master that gives comprehensive questions from the given context. Based on your experience, please provide me with a question that resembles a general or summary question in research style."
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    exp_hm_input = "Vietnam lies between 8 o 30 N - 23 o 02 N, stretching from Lung Cu village (Dong Van district, Ha Giang province) in the North to Mui hamlet (Nam Can district, Ca Mau province) in the South. The length of the country is about four times that of its width. Its widest point is around 500 km (Mong Cai, Quang Ninh - Dien Bien) while the narrowest point is only 50 km wide (the frontier of Viet - Laos to Dong Hoi, Quang Binh province) (Fig. 1.1 and 1.2). Vietnam’s mainland covers 329,229 km2."
    exp_ai_rsp = "question +++ What is the geographical span of Vietnam, including its northernmost and southernmost points, as well as its widest and narrowest points? ----- answer +++ The approximate width of Vietnam at its narrowest point is 50 km (from the frontier of Viet-Laos to Dong Hoi, Quang Binh province), while its widest point is around 500 km (from Mong Cai, Quang Ninh to Dien Bien)."
    example_human = HumanMessagePromptTemplate.from_template(exp_hm_input)
    example_ai = AIMessagePromptTemplate.from_template(exp_ai_rsp)
    human_template = "{text}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    # combine all the prompts into one
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, example_human, example_ai, human_message_prompt]
    )
    # create a chain
    chain = LLMChain(llm=chat, prompt=chat_prompt)
    # get a chat completion from the formatted messages
    result = chain.run(context)
    # split the result into the question and answer
    _question = result.split("-----")[0].split("+++")[1].strip()
    _answer = result.split("-----")[1].split("+++")[1].strip()

    return _question, _answer
    
def save_qadb(_question:str, _answer:str):
    #check if /qadb/qadb.json is file
    qadb_path = "qadb/qadb.json"
    if os.path.isfile(qadb_path):
        #load qadb.json file as a dict
        _qadb = json.load(open(qadb_path, "r"))
    else:
        #create a new dict
        _qadb = {}
        
    # check length of _qadb
    _question_order = len(_qadb)
    # add new question to _qadb dictionary
    _qadb[_question_order] = {"question": _question, "answer": _answer}
    #dump _qadb overwrite "/qadb/qadb.json" file
    json.dump(_qadb, open(qadb_path, "w"))
    print("Saved to qadb/qadb.json")
    st.success("Saved to database")
    
def read_fact_db():
    #check if /qadb/qadb.json is file
    qadb_path = "qadb/qadb.json"
    if os.path.isfile(qadb_path):
        #load qadb.json file as a dict
        _qadb = json.load(open(qadb_path, "r"))
        #create a pandas df from _qadb
        _qadb_df = pd.DataFrame.from_dict(_qadb, orient="index")
        st.dataframe(_qadb_df, use_container_width=True,
                       column_config={"question": st.column_config.TextColumn(width='large',
                                                                              ),
                                      "answer": st.column_config.TextColumn(width='large',
                                                                              ),
                                      }
                       )
    else:
        st.info("No facts database found")
        pass
    
# context = "Outside its mainland territory, Vietnam has a continental shelf, and thousands of islands and archipelagoes such as those in the Gulf of Bac Bo (before named the gulf of Tonkin), the Hoang Sa (Paracel) and Truong Sa (Spratly) Archipelagoes in the East Sea, and the Tho Chu, Phu Quoc islands in the Gulf of Thailand. Two thirds of Vietnam’s territory is covered with hills and mountains. The most mountainous area belongs to the northwest, from the upper reaches of Ma River to the Red river valley. The Fansipan summit, at 3,148m, is the highest peak in the Indochina. The Viet Bac Mountains, located on Chay River’s right bank and terminated at the Red river valley, are made up of such peaks as Tay Con Linh (2,431 m high), and Kieu Lieu Ti (2,402 m). The northeastern hills-mountains, spreading from Lo river valley to coastal area of Quang Ninh province, are bow-shaped ranges protruding to the sea (Gam River, Yen Lac, Bac Son, and Dong Trieu bows). The Truong Son mountain range, exten-ding from the southern part of Xieng Khoang plateau (Laos) to the southern part of Central Vietnam, consists of Pu Lai Leng peak (2,711m), Rao Co (2,335 m), and Ngoc Linh, Ngoc Niay, Ngoc Pan, Ngoc Kring peaks; The Lam Vien, Bao Loc, and Di Linh and Mnong plateaus shape a plateau massif at the southern tip of Vietnam."
main()