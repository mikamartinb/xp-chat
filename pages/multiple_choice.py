import streamlit as st
import random
from SQLmodule_commands import get_all_mtl_questions, get_all_lectures
from model_utils import initialize_model

# llm = initialize_model()

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
    st.page_link("pages/home.py", label="Home", icon="🏠")
    st.page_link("pages/stats.py", label="Meine Statistik", icon="📊")
    st.write("Lernen")
    st.page_link("pages/multiple_choice.py", label="Multiple Choice", icon="🔘")
    st.page_link("pages/open_questions.py", label="Open Questions", icon="📝")
    st.page_link("pages/chatting.py", label="Chatten", icon="💬")
    st.divider()
    if st.session_state.get("is_admin", True):
        st.page_link("pages/admin.py", label="Rüsselraum", icon="🔒")
    st.page_link("pages/user_einstellung.py", label="User Einstellungen", icon="⚙️")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.toast("Erfolgreich abgemeldet.", icon='👋')
        st.switch_page("app.py")
    st.sidebar.markdown("Made with 💙")

# Initialisierung des Testmodus in der Session-State
if 'test_mode' not in st.session_state:
    st.session_state.test_mode = False

# Dialogfunktion zum Aktivieren des Testmodus
@st.dialog("Testmodus aktivieren", width="small")
def activate_test_mode_dialog():
    st.write("Bist du sicher, dass du den Testmodus starten möchtest? Deine Antworten wirken sich auf deine globale Statistik im Scoreboard aus.")
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("Ja, aktivieren"):
            st.session_state.test_mode = True
            st.toast("Testmodus aktiviert!")
            st.rerun()

# Dialogfunktion zum Verlassen des Testmodus
@st.dialog("Testmodus verlassen", width="small")
def deactivate_test_mode_dialog():
    st.write("Bist du sicher, dass du den Testmodus verlassen möchtest?")
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button("Ja, verlassen"):
            st.session_state.test_mode = False
            st.toast("Testmodus deaktiviert!")
            st.rerun()

# Button zum Umschalten des Testmodus
col1, col2, col3 = st.columns(3)
with col2:
    if st.session_state.test_mode:
        # Wenn der Testmodus aktiv ist, wird der Deaktivierungsdialog angezeigt
        if st.button("Testmodus verlassen"):
            deactivate_test_mode_dialog()
    else:
        # Wenn der Testmodus inaktiv ist, wird der Aktivierungsdialog angezeigt
        if st.button("Testmodus starten"):
            activate_test_mode_dialog()

# CSS zum Anpassen der Logo-Größe
st.markdown(
    """
    <style>
    div[data-testid="stSidebarHeader"] img.stLogo{
        height: auto;
        width: auto;
    }
    div[data-testid="stSidebarCollapsedControl"] img.stLogo {
        height: 100px;
        width: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Überschrift für den Modus
if st.session_state.test_mode:
    st.markdown("<h1 style='text-align: center; color: white;'>TESTMODUS</h1>", unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align: center; color: white;'>Modus: Multiple Choice 🔘</h1>", unsafe_allow_html=True)

# Lade die Fragenliste und mische sie
questions = get_all_mtl_questions()
random.shuffle(questions)

lectures = get_all_lectures()
lecture_titles = [lec.title for lec in lectures]

# Wenn Testmodus, Multiselect ausblenden
if not st.session_state.test_mode:
    # Auswahl der gefilterten Vorlesungen
    selected_lecture_titles = st.multiselect(
        "Vorlesungen auswählen",  
        lecture_titles,
        [],
        placeholder="Wähle eine oder mehrere Vorlesungen",
        label_visibility="collapsed"  
    )
else:
    # Im Testmodus müssen keine Vorlesungen ausgewählt werden
    selected_lecture_titles = lecture_titles  # Alle Vorlesungen werden automatisch verwendet

# Filtern der lecture_ids basierend auf den ausgewählten Titeln
selected_lecture_ids = [
    lec.id for lec in lectures if lec.title in selected_lecture_titles
]

# Filtern der Fragen basierend auf den ausgewählten lecture_ids (auch im Testmodus, alle Fragen anzeigen)
filtered_questions = [
    question for question in questions if question.lecture_id in selected_lecture_ids or st.session_state.test_mode
]

# Hinweis anzeigen, falls keine Fragen vorhanden sind
if not filtered_questions:
    st.warning("Keine Fragen vorhanden!")
else:
    # Initialisiere session_state Variablen, falls nicht vorhanden
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

    # Funktion zum Quiz neu starten
    def restart_quiz():
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.selected_option = None
        st.session_state.answer_submitted = False
        random.shuffle(filtered_questions)

        st.session_state.shuffled_options = []
        st.session_state.current_question = filtered_questions[st.session_state.current_index]
        st.session_state.options_shuffled = False  
        shuffle_options()

    # Funktion zum Mischen der Optionen
    def shuffle_options():
        options = [
            getattr(st.session_state.current_question, f"options_{i}")
            for i in range(1, 5)
            if getattr(st.session_state.current_question, f"options_{i}", None)
        ]
        random.shuffle(options) 
        st.session_state.shuffled_options = options
        correct_answer_option = getattr(
            st.session_state.current_question,
            f"options_{st.session_state.current_question.answer[-1]}"
        )
        st.session_state.correct_answer = options.index(correct_answer_option)
        
        st.session_state.options_shuffled = True

    if not st.session_state.options_shuffled:
        shuffle_options()

    # Funktion zur Antwortabgabe
    def submit_answer():
        if st.session_state.selected_option is not None:
            st.session_state.answer_submitted = True
            correct_index = st.session_state.correct_answer
            if st.session_state.selected_option == correct_index:
                st.session_state.score += 10
        else:
            st.warning("Bitte wählen Sie eine Option aus, bevor Sie sie absenden.")

    # Funktion für die nächste Frage
    def next_question():
        st.session_state.current_index += 1
        if st.session_state.current_index < len(filtered_questions):
            st.session_state.selected_option = None
            st.session_state.answer_submitted = False
            st.session_state.current_question = filtered_questions[st.session_state.current_index]
            st.session_state.options_shuffled = False
        else:
            st.write(f"Quiz beendet! Ihr Endergebnis ist: {st.session_state.score} / {len(filtered_questions) * 10}")
            st.button('Neu starten', on_click=restart_quiz)

    # Quiz-Fortschritt
    progress_bar_value = (st.session_state.current_index + 1) / len(filtered_questions)
    st.metric(label="Score", value=f"{st.session_state.score} / {len(filtered_questions) * 10}")
    st.progress(progress_bar_value)

    # Anzeige der aktuellen Frage
    current_question = st.session_state.current_question
    col1, col2, col3 = st.columns(3)
    with col2:  
        st.subheader(f"Frage {st.session_state.current_index + 1}")
    st.write(current_question.question_text)

    # Anzeige der gemischten Optionen
    for i, option in enumerate(st.session_state.shuffled_options):
        if st.session_state.answer_submitted:
            if i == st.session_state.correct_answer:
                st.success(f"{option} (Richtige Antwort)")
            elif i == st.session_state.selected_option:
                st.error(f"{option} (Falsche Antwort)")
            else:
                st.write(option)
        else:
            if st.button(option, key=f"option_{i}"):
                st.session_state.selected_option = i

    # Aktionen abhängig vom Zustand
    if st.session_state.answer_submitted:
        if st.button("Weiter"):
            next_question()
    else:
        if st.button("Antwort absenden"):
            submit_answer()
