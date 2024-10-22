import streamlit as st

st.page_link("chatbot.py", label="Back to options")

st.title('Modus: Chatting')

messages = st.container(height=300)
if prompt := st.chat_input("Say something"):
    messages.chat_message("user").write(prompt)
    messages.chat_message("assistant").write(f"Echo: {prompt}")