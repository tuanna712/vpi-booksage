import streamlit as st
from ui.ui_facts_multiple_questions import *
from ui.ui_facts_gen import *
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
        if 'user_email' not in st.session_state:
            user_name = st.text_input(label='Enter your email:',
                                        value='vpi_user_name@vpi.pvn.vn',
                                        key='defined_email_2')
            st.session_state.user_email = user_name
        # Check if user is logged in---------------------------
        if 'user_email' in st.session_state:
            st.write(f"User: {st.session_state.user_email}")
            USER = st.session_state.user_email.split('@')[0]
            FACTS_JSON = os.getcwd() + '/' + f'database/{USER}/facts_db/txt_db/qadb.json'
            FACTS_DB = os.getcwd() + '/' + f'database/{USER}/facts_db/facts_vector_db'
            os.makedirs(os.path.dirname(FACTS_JSON), exist_ok=True)
            os.makedirs(os.path.dirname(FACTS_DB), exist_ok=True)
        else:
            st.warning("Please login first")
            st.stop()
            
        # --- TABS Definition ---------------------------------
        fact_ui_options = st.radio('Facts UI', ['Single Question', 'Multiple Questions'], 
                                   key='fact_ui_options')
    # --- Single Question --------------------------------------
    if fact_ui_options == 'Single Question':
        subtab1, subtab2, subtab3, subtab4 = st.tabs(['Generator', 'Review', 'Edit', 'Database'])
        # --- UI Generator -------------------------------------
        with subtab1:
            ui_facts_gen(FACTS_JSON)
        # --- UI Review ----------------------------------------
        with subtab2:
            read_df = read_fact_db(FACTS_JSON)
            display_single_fact(read_df)
        # --- UI Edit ------------------------------------------
        with subtab3:
            read_df = read_fact_db(FACTS_JSON)
            edit_fact_db(read_df, FACTS_JSON)
        # --- UI Database --------------------------------------
        with subtab4:
            facts_to_vectordb(FACTS_DB, FACTS_JSON)
    # --- Multiple Questions -----------------------------------
    if fact_ui_options == 'Multiple Questions':
        ui_multiple_questions(FACTS_DB)

main()