import streamlit as st
from model_utils import initialize_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

st.set_page_config(initial_sidebar_state="collapsed")
st.title("_:blue[XP]Chat_")

st.markdown("*Choose your learning modus*")
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(height=300, border=False):
        st.page_link("pages/multiple_choice.py", label="Modus 1: Multiple Choice", icon="🔘")
        # st.image("images/multiple_choice.png", use_column_width=True)

with col2:
    with st.container(height=300, border=False):
        st.page_link("pages/open_questions.py", label="Modus 2: Open Questions", icon="📝")
        #st.image("images/open_question.png", use_column_width=True)

with col3:
    with st.container(height=300, border=False):
        st.page_link("pages/chatting.py", label="Modus 3. Chatting", icon="💬")
        #st.image("images/chatting.png", use_column_width=True)