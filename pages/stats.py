import streamlit as st
import plotly.express as px
from streamlit_plotly_events import plotly_events
from SQLmodule_commands import(
    get_user_progress,
    get_not_answered_questions,
    get_wrong_questions,
    get_one_to_two_correct_questions,
    get_three_or_more_correct_questions,
)


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

with st.sidebar:
    #st.logo("")
    st.header("Herzlich Willkommen!", divider="red")
    st.page_link("pages/home.py",label="Home", icon="🏠")
    st.page_link("pages/stats.py",label="Meine Statistik", icon="📊")
    st.write("Lernen")
    st.page_link("pages/multiple_choice.py",label="Multiple Choice", icon="🔘")
    st.page_link("pages/open_questions.py",label="Open Questions", icon="📝")
    st.page_link("pages/chatting.py",label="Chatten", icon="💬")
    st.divider()
    # Admin-Seite nur hinzufügen, wenn der Benutzer Admin-Rechte hat
    if st.session_state.get("is_admin", True):
        st.page_link("pages/admin.py",label="Admin", icon="🔒")
    st.page_link("pages/user_einstellung.py",label="User Einstellungen", icon="⚙️")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.toast("Erfolgreich abgemeldet.", icon='👋')
        st.switch_page("app.py")
    st.sidebar.markdown("Made with ❤️ by ChatXP")

# --- Titel und Beschreibung ---
st.title("Meine Statistik")

# --- Daten abrufen ---
matrikelnummer = st.session_state.matrikelnummer
progress_data = get_user_progress(matrikelnummer)

# --- Daten für das Pie Chart ---
categories = list(progress_data.keys())
counts = list(progress_data.values())
total_questions = sum(counts)

# --- Pie Chart erstellen ---
fig = px.pie(
    values=counts,
    names=categories,
    title=f"Lernfortschritt aus {total_questions} Multiple-Choice-Fragen",
    color=categories,
    color_discrete_map={
        "Noch nicht beantwortet": "gray",
        "Falsch beantwortet": "red",
        "1-2 richtig beantwortet": "yellow",
        "3-mal richtig beantwortet": "green",
    },
)

# Anpassungen des Texts im Diagramm und Hover-Text
fig.update_traces(
    textinfo="percent",  # Zeigt den Prozentwert im Diagramm an
    textfont=dict(color="black"),  # Textfarbe innerhalb des Diagramms auf Schwarz setzen
    hovertemplate="%{value} Fragen",  # Nur die Anzahl der Fragen im Hover-Text anzeigen
    hoverlabel=dict(font=dict(color="black")),  # Schriftfarbe des Hover-Textes auf Schwarz setzen
)

# Hintergrund und allgemeine Textfarbe anpassen
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",  # Hintergrund des Diagrammbereichs transparent
    paper_bgcolor="rgba(0,0,0,0)",  # Hintergrund des gesamten Graphen transparent
    font=dict(color="black"),  # Textfarbe im gesamten Diagramm auf Schwarz setzen
    title_font=dict(size=18),  # Optional: Schriftgröße des Titels
)

# --- Chart interaktiv anzeigen und Klick-Ereignisse erfassen ---
ausgewählte_punkte = plotly_events(fig, click_event=True)

@st.dialog("Noch nicht beantwortete Fragen", width="large")
def zeige_nicht_beantwortet():
    matrikelnummer = st.session_state.get("matrikelnummer")
    not_answered_questions = get_not_answered_questions(matrikelnummer)

    if not_answered_questions:
        # Gruppieren der Fragen nach Vorlesung
        lectures_questions = {}
        for item in not_answered_questions:
            lecture_title = item["lecture_title"]
            question = item["question"]
            if lecture_title not in lectures_questions:
                lectures_questions[lecture_title] = []
            lectures_questions[lecture_title].append(question)

        # Sortieren der Vorlesungen nach Titel (z. B. 00, 01, ...)
        sorted_lectures = sorted(lectures_questions.items(), key=lambda x: x[0])

        # Anzeigen der Fragen gruppiert nach Vorlesung
        for lecture_title, questions in sorted_lectures:
            with st.expander(f"Vorlesung: {lecture_title}", expanded=False):
                for question in questions:
                    with st.container(border=True):
                        st.write(f"**Frage {question.id}:** {question.question_text}")
                        st.write(f"- Option 1: {question.options_1}")
                        st.write(f"- Option 2: {question.options_2}")
                        st.write(f"- Option 3: {question.options_3}")
                        st.write(f"- Option 4: {question.options_4}")
        if st.button("Sofort Weiter Lernen!!!", type="primary"):
            st.switch_page("pages/multiple_choice.py")

    else:
        st.info("Alle Fragen wurden beantwortet.")




@st.dialog("Falsch beantwortete Fragen", width="large")
def zeige_falsch_beantwortet():
    matrikelnummer = st.session_state.get("matrikelnummer")
    wrong_questions = get_wrong_questions(matrikelnummer)

    if wrong_questions:
        # Gruppieren der Fragen nach Vorlesung
        lectures_questions = {}
        for item in wrong_questions:
            lecture_title = item["lecture_title"]
            question = item["question"]
            if lecture_title not in lectures_questions:
                lectures_questions[lecture_title] = []
            lectures_questions[lecture_title].append(question)

        # Sortieren der Vorlesungen nach Titel (z. B. 00, 01, ...)
        sorted_lectures = sorted(lectures_questions.items(), key=lambda x: x[0])

        # Anzeigen der Fragen gruppiert nach Vorlesung
        for lecture_title, questions in sorted_lectures:
            with st.expander(f"Vorlesung: {lecture_title}", expanded=False):
                for question in questions:
                    with st.container(border=True):
                        st.write(f"**Frage {question.id}:** {question.question_text}")
                        st.write(f"- Option 1: {question.options_1}")
                        st.write(f"- Option 2: {question.options_2}")
                        st.write(f"- Option 3: {question.options_3}")
                        st.write(f"- Option 4: {question.options_4}")
        if st.button("Sofort Weiter Lernen!!!", type="primary"):
            st.switch_page("pages/multiple_choice.py")
    else:
        st.info("Keine falsch beantworteten Fragen vorhanden.")


@st.dialog("1-2 richtig beantwortete Fragen", width="large")
def zeige_eins_bis_zwei_richtig():
    matrikelnummer = st.session_state.get("matrikelnummer")
    one_to_two_questions = get_one_to_two_correct_questions(matrikelnummer)

    if one_to_two_questions:
        # Gruppieren der Fragen nach Vorlesung
        lectures_questions = {}
        for item in one_to_two_questions:
            lecture_title = item["lecture_title"]
            question = item["question"]
            if lecture_title not in lectures_questions:
                lectures_questions[lecture_title] = []
            lectures_questions[lecture_title].append(question)

        # Sortieren der Vorlesungen nach Titel (z. B. 00, 01, ...)
        sorted_lectures = sorted(lectures_questions.items(), key=lambda x: x[0])

        # Anzeigen der Fragen gruppiert nach Vorlesung
        for lecture_title, questions in sorted_lectures:
            with st.expander(f"Vorlesung: {lecture_title}", expanded=False):
                for question in questions:
                    with st.container(border=True):
                        st.write(f"**Frage {question.id}:** {question.question_text}")
                        st.write(f"- Option 1: {question.options_1}")
                        st.write(f"- Option 2: {question.options_2}")
                        st.write(f"- Option 3: {question.options_3}")
                        st.write(f"- Option 4: {question.options_4}")
        if st.button("Sofort Weiter Lernen!!!", type="primary"):
            st.switch_page("pages/multiple_choice.py")
    else:
        st.info("Keine 1-2 Mal richtig beantworteten Fragen vorhanden.")


@st.dialog("3-mal richtig beantwortete Fragen", width="large")
def zeige_drei_oder_mehr_richtig():
    matrikelnummer = st.session_state.get("matrikelnummer")
    three_or_more_questions = get_three_or_more_correct_questions(matrikelnummer)

    if three_or_more_questions:
        # Gruppieren der Fragen nach Vorlesung
        lectures_questions = {}
        for item in three_or_more_questions:
            lecture_title = item["lecture_title"]
            question = item["question"]
            if lecture_title not in lectures_questions:
                lectures_questions[lecture_title] = []
            lectures_questions[lecture_title].append(question)

        # Sortieren der Vorlesungen nach Titel (z. B. 00, 01, ...)
        sorted_lectures = sorted(lectures_questions.items(), key=lambda x: x[0])

        # Anzeigen der Fragen gruppiert nach Vorlesung
        for lecture_title, questions in sorted_lectures:
            with st.expander(f"Vorlesung: {lecture_title}", expanded=False):
                for question in questions:
                    with st.container(border=True):
                        st.write(f"**Frage {question.id}:** {question.question_text}")
                        st.write(f"- Option 1: {question.options_1}")
                        st.write(f"- Option 2: {question.options_2}")
                        st.write(f"- Option 3: {question.options_3}")
                        st.write(f"- Option 4: {question.options_4}")
        if st.button("Sofort Weiter Lernen!!!", type="primary"):
            st.switch_page("pages/multiple_choice.py")
    else:
        st.info("Keine 3-mal oder häufiger richtig beantworteten Fragen vorhanden.")


# Überprüfen, ob ein Segment angeklickt wurde
if ausgewählte_punkte:
    # Extrahieren des Indexes des angeklickten Segments
    punkt_index = ausgewählte_punkte[0]['pointNumber']
    
    # Überprüfen, ob der Index innerhalb des gültigen Bereichs liegt
    if 0 <= punkt_index < len(categories):
        # Bestimmen der angeklickten Kategorie basierend auf dem Index
        angeklickte_kategorie = categories[punkt_index]
        
        # Entsprechend der angeklickten Kategorie die jeweilige Funktion aufrufen
        if angeklickte_kategorie == "Noch nicht beantwortet":
            zeige_nicht_beantwortet()
        elif angeklickte_kategorie == "Falsch beantwortet":
            zeige_falsch_beantwortet()
        elif angeklickte_kategorie == "1-2 richtig beantwortet":
            zeige_eins_bis_zwei_richtig()
        elif angeklickte_kategorie == "3-mal richtig beantwortet":
            zeige_drei_oder_mehr_richtig()
    else:
        st.error("Ungültiger Index für das angeklickte Segment.")

