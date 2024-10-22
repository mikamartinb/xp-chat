import streamlit as st

st.page_link("chatbot.py", label="Back to options")

st.title('Modus: Open Questions')

st.write("This is a sample question?")

prompt = st.chat_input("Say something")