import streamlit as st
import random
from SQLmodule_commands import get_all_mtl_questions, get_all_lectures
from model_utils import initialize_model
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser

llm = initialize_model()

st.set_page_config(
    page_title="Home",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.google.com',
        'Report a bug': "https://www.google.com",
        'About': "# Viel Spaß! Beim Lernen für die WI-Prüfung"
    }
)

# --- Sidebar ---
with st.sidebar:
    st.logo(
        image="images/Logo_LerniPhant_500x500-removebg.png",
        icon_image="images/Elefant.png"
    )
    st.header("Herzlich Willkommen!", divider="blue")
    st.page_link("pages/home.py",label="Home", icon="🏠")
    st.page_link("pages/stats.py",label="Meine Statistik", icon="📊")
    st.write("Lernen")
    st.page_link("pages/multiple_choice.py",label="Multiple Choice", icon="🔘")
    st.page_link("pages/open_questions.py",label="Open Questions", icon="📝")
    st.page_link("pages/chatting.py",label="Chatten", icon="💬")
    st.divider()
    # Admin-Seite nur hinzufügen, wenn der Benutzer Admin-Rechte hat
    if st.session_state.get("is_admin", True):
        st.page_link("pages/admin.py",label="Rüsselraum", icon="🔒")
    st.page_link("pages/user_einstellung.py",label="User Einstellungen", icon="⚙️")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.toast("Erfolgreich abgemeldet.", icon='👋')
        st.switch_page("app.py")
    st.sidebar.markdown("Made with 💙")

# CSS zum Anpassen der Logo-Größe
st.markdown(
    """
    <style>
    /* Anpassung des Logos in der Sidebar */
    div[data-testid="stSidebarHeader"] img.stLogo{
        height: auto; /* Gewünschte Höhe des Logos */
        width: auto;   /* Automatische Anpassung der Breite */
    }
    /* Anpassung des Logos in der oberen linken Ecke */
    div[data-testid="stSidebarCollapsedControl"] img.stLogo {
        height: 100px; /* Gewünschte Höhe des Icons */
        width: auto;  /* Automatische Anpassung der Breite */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='text-align: center; color: white;'>Modus: Multiple Choice 🔘</h1>", unsafe_allow_html=True)

# Lade die Fragenliste und mische sie
questions = get_all_mtl_questions()
random.shuffle(questions)  # Mischt die Reihenfolge der Fragen

lectures = get_all_lectures()
lecture_titles = [lec.title for lec in lectures]

# Auswahl der gefilterten Vorlesungen
selected_lecture_titles = st.multiselect(
    "Vorlesungen auswählen",  # Gib ein Label an, das für Barrierefreiheit verwendet wird
    lecture_titles,
    [],
    placeholder="Wähle eine oder mehrere Vorlesungen",
    label_visibility="collapsed"  # Das Label wird versteckt
)


# Filtern der lecture_ids basierend auf den ausgewählten Titeln
selected_lecture_ids = [
    lec.id for lec in lectures if lec.title in selected_lecture_titles
]

# Filtern der Fragen basierend auf den ausgewählten lecture_ids
filtered_questions = [
    question for question in questions if question.lecture_id in selected_lecture_ids
]

# Hinweis anzeigen, falls keine Fragen vorhanden sind
if not filtered_questions:
    st.warning("Keine Vorlesung ausgewählt!")
else:
    # Initialize session state variables if they don't exist
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'selected_option' not in st.session_state:
        st.session_state.selected_option = None
    if 'answer_submitted' not in st.session_state:
        st.session_state.answer_submitted = False
    if 'shuffled_options' not in st.session_state:
        st.session_state.shuffled_options = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = filtered_questions[st.session_state.current_index]
    if 'options_shuffled' not in st.session_state:
        st.session_state.options_shuffled = False

    # Function to reset quiz
    def restart_quiz():
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.selected_option = None
        st.session_state.answer_submitted = False
        random.shuffle(filtered_questions)  # Mischt die Fragen bei jedem Neustart

        #TODO
        # for question in filtered_questions:
        #     question.question_text = rephrase_question_with_llm(question.question_text)

        st.session_state.shuffled_options = []
        st.session_state.current_question = filtered_questions[st.session_state.current_index]
        st.session_state.options_shuffled = False  # Reset shuffle flag for the first question
        shuffle_options()  # Optionen für die erste Frage mischen


    # Function to shuffle options for the current question
    def shuffle_options():
        options = [
            getattr(st.session_state.current_question, f"options_{i}")
            for i in range(1, 5)
            if getattr(st.session_state.current_question, f"options_{i}", None)
        ]  # Dynamische Optionen-Liste
        random.shuffle(options) 
        st.session_state.shuffled_options = options
        correct_answer_option = getattr(
            st.session_state.current_question,
            f"options_{st.session_state.current_question.answer[-1]}"
        )
        st.session_state.correct_answer = options.index(correct_answer_option)
        
        #TODO: options = rephrase_answers_with_llm(question=st.session_state.current_question, options=options)
        
        st.session_state.options_shuffled = True  # Set shuffle flag to True after shuffling

    # Load the first question and shuffle options if no question is loaded
    if not st.session_state.options_shuffled:
        shuffle_options()

    # Function to submit an answer
    def submit_answer():
        if st.session_state.selected_option is not None:
            st.session_state.answer_submitted = True
            correct_index = st.session_state.correct_answer
            if st.session_state.selected_option == correct_index:
                st.session_state.score += 10
        else:
            st.warning("Bitte wählen Sie eine Option aus, bevor Sie sie absenden.")

    # Function to move to the next question
    def next_question():
        st.session_state.current_index += 1
        if st.session_state.current_index < len(filtered_questions):
            st.session_state.selected_option = None
            st.session_state.answer_submitted = False
            st.session_state.current_question = filtered_questions[st.session_state.current_index]
            st.session_state.options_shuffled = False  # Reset shuffle flag for new question
        else:
            st.write(f"Quiz beendet! Ihr Endergebnis ist: {st.session_state.score} / {len(filtered_questions) * 10}")
            st.button('Neu starten', on_click=restart_quiz)

    # Quiz progress
    progress_bar_value = (st.session_state.current_index + 1) / len(filtered_questions)
    st.metric(label="Score", value=f"{st.session_state.score} / {len(filtered_questions) * 10}")
    st.progress(progress_bar_value)

    # Display current question
    current_question = st.session_state.current_question
    st.subheader(f"Frage {st.session_state.current_index + 1}")
    st.write(current_question.question_text)

    # Display shuffled options
    for i, option in enumerate(st.session_state.shuffled_options):
        if st.session_state.answer_submitted:
            if i == st.session_state.correct_answer:
                st.success(f"{option} (Richtige Antwort)")
            elif i == st.session_state.selected_option:
                st.error(f"{option} (Falsche Antwort)")
            else:
                st.write(option)
        else:
            if st.button(option):
                st.session_state.selected_option = i

    # Submission and next question buttons
    if st.session_state.answer_submitted:
        if st.session_state.current_index < len(filtered_questions) - 1:
            st.button('Nächste Frage', on_click=next_question)
        else:
            st.write(f"Quiz beendet! Ihr Endergebnis ist: {st.session_state.score} / {len(filtered_questions) * 10}")
            st.button('Neu starten', on_click=restart_quiz)
    else:
        st.button('Absenden', on_click=submit_answer)