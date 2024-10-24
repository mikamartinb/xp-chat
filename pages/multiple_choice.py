import streamlit as st
import json

st.page_link("Home.py", icon="⬅️")

st.markdown("<h1 style='text-align: center; color: white;'>Modus: Multiple Choice 🔘</h1>", unsafe_allow_html=True)

# Custom CSS for button styling
st.markdown("""
    <style>
    div.stButton > button:first-child {
        display: block;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

# Load the quiz data from the JSON file
quiz_file_path = '/Users/mika/Desktop/Mika/Studium/7.Semester/AI Project/xp-chat-1/questions_answers/multiple_choice.json'

# Load quiz data from JSON file (assuming it’s a list of questions)
with open(quiz_file_path, 'r', encoding='utf-8') as f:
    quiz_data = json.load(f)

# Initialize session state variables if they don't exist
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None
if 'answer_submitted' not in st.session_state:
    st.session_state.answer_submitted = False

# Function to reset quiz
def restart_quiz():
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.selected_option = None
    st.session_state.answer_submitted = False

# Function to submit an answer
def submit_answer():
    # Check if an option has been selected
    if st.session_state.selected_option is not None:
        st.session_state.answer_submitted = True
        # Check if the selected option is correct
        correct_answer = quiz_data[st.session_state.current_index]['answer']
        if st.session_state.selected_option == correct_answer:
            st.session_state.score += 10
    else:
        # Show a warning if no option has been selected
        st.warning("Please select an option before submitting.")

# Function to move to the next question
def next_question():
    st.session_state.current_index += 1
    st.session_state.selected_option = None
    st.session_state.answer_submitted = False

# Quiz progress
progress_bar_value = (st.session_state.current_index + 1) / len(quiz_data)
st.metric(label="Score", value=f"{st.session_state.score} / {len(quiz_data) * 10}")
st.progress(progress_bar_value)

# Display current question
question_item = quiz_data[st.session_state.current_index]
st.subheader(f"Question {st.session_state.current_index + 1}")
st.write(question_item['question'])
st.write(question_item['information'])

# Display options as buttons
options = question_item['options']
correct_answer = question_item['answer']

if st.session_state.answer_submitted:
    # Display the feedback for the selected answer
    for option in options:
        if option == correct_answer:
            st.success(f"{option} (Correct answer)")
        elif option == st.session_state.selected_option:
            st.error(f"{option} (Incorrect answer)")
        else:
            st.write(option)
else:
    for option in options:
        if st.button(option):
            st.session_state.selected_option = option

# Submission and next question buttons
if st.session_state.answer_submitted:
    if st.session_state.current_index < len(quiz_data) - 1:
        st.button('Next', on_click=next_question)
    else:
        st.write(f"Quiz completed! Your final score is: {st.session_state.score} / {len(quiz_data) * 10}")
        st.button('Restart', on_click=restart_quiz)
else:
    st.button('Submit', on_click=submit_answer)
