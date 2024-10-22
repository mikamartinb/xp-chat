import streamlit as st

st.page_link("chatbot.py", label="Back to options")

st.title('Modus: Multiple Choice')

st.write("This is a sample question?")

st.checkbox(
    "Answer1"
)
st.checkbox(
    "Answer2"
)
st.checkbox(
    "Answer3"
)

st.button(
    "Submit"
)