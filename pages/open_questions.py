import streamlit as st

st.page_link("Home.py", icon="⬅️")

st.markdown("<h1 style='text-align: center; color: white;'>Modus: Open Questions 📝</h1>", unsafe_allow_html=True)

st.write("This is a sample question?")

prompt = st.chat_input("Say something")