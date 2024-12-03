import streamlit as st
from sqlmodel import Session, select, create_engine, delete
import json
import pandas as pd
import numpy as np
import time
from SQLmodule_commands import (
    create_tables, add_user_in_admin, get_unregistered_matrikelnummern, get_registered_user_ids,
    add_unregistered_matrikelnummern, delete_erlaubte_matrikelnummer, # Importiert Matrieklnummern Funktionen
    get_all_users_info, update_all_users_info, delete_user_completly, # Importiert User Funktionen
    get_all_lectures, add_lecture, update_lecture, delete_lecture, # Importiert Vorlesungs Funktionen
    get_all_mtl_questions, add_mtl_question, update_mtl_question, delete_mtl_question # Importiert Multiple Choice Fragen Funktionen
)

# --- Seitenkonfiguration ---
st.set_page_config(
    page_title="Rüsselraum",
    page_icon="🔒",
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
    st.sidebar.markdown("Made with 💙 by ChatXP")

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

#color = st.get_option("theme.primaryColor") #Überlegung alle Farbe änderung damit zu ersetzen falls man später theme color ändern will

# --- Page Content ---
st.title(":blue[Rüsselraum] Dashboard :lock:")

# --- Dashboard ---
col1, col2, col3 = st.columns(3) 
col1.metric("User", "70 °F", "-1.2 °F") #User Anzahl sollte akutelle angezeigt werden 
col2.metric("Wind", "9 mph", "-8%")
col3.metric("Humidity", "86%", "4%")

# Manuelles hinzufügen von Usern
def registration_page():
    # Formular für die Registrierung
    with st.form(key='Registrierung', clear_on_submit=True):
        matrikelnummer = st.text_input("Matrikelnummer", placeholder="Die Matrikelnummer wird automatisch zugelassen")
        vorname = st.text_input("Vorname", placeholder="z.B. Max")
        nachname = st.text_input("Nachname", placeholder="z.B. Mustermann")
        email = st.text_input("E-Mail", placeholder="z.B. max-mustermann@gmail.com")
        passwort = st.text_input("Passwort", placeholder="z.B. Max!1234", type="password")
        is_user_admin = st.checkbox("Soll der user :red[Admin] recht haben?")
        submit_button = st.form_submit_button("User Ersetellen", type="primary") 
    # Funktion zur Überprüfung der E-Mail-Adresse
    def is_valid_email(email):
        # Überprüfen auf genau ein "@"-Zeichen
        if email.count("@") != 1:
            st.error("Eine E-Mail Adresse muss genau ein @ enthalten!", icon="📧")
            return False
        # Lokalen und Domain-Teil aufteilen
        local, domain = email.split("@")
        # Überprüfen, dass beide Teile nicht leer sind
        if not local or not domain:
            st.error("Der lokale oder Domain-Teil der E-Mail-Adresse darf nicht leer sein", icon="📧")
            return False
        # Überprüfen, dass der lokale Teil nur Buchstaben, Zahlen und erlaubte Sonderzeichen enthält
        allowed_local_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&'*+-/=?^_`{|}~.")
        if any(char not in allowed_local_chars for char in local):
            st.error("Der lokale Teil der E-Mail-Adresse enthält ungültige Zeichen", icon="📧")
            return False
        # Lokaler Teil darf nicht mit Punkt beginnen oder enden und keine aufeinanderfolgenden Punkte enthalten
        if local[0] == "." or local[-1] == "." or ".." in local:
            st.error("Der lokale Teil der E-Mail-Adresse darf nicht mit Punkt beginnen oder enden und keine aufeinanderfolgenden Punkte enthalten", icon="📧")
            return False
        # Domain-Teil überprüfen (muss mindestens einen Punkt enthalten und darf nicht mit Punkt beginnen oder enden)
        if domain.count(".") < 1 or domain[0] == "." or domain[-1] == ".":
            st.error("Der Domain-Teil der E-Mail-Adresse muss mindestens einen Punkt enthalten und darf nicht mit Punkt beginnen oder enden", icon="📧")
            return False
        # Jeder Teil der Domain muss nur Buchstaben und Zahlen enthalten
        domain_parts = domain.split(".")
        allowed_domain_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")
        for part in domain_parts:
            if not part or any(char not in allowed_domain_chars for char in part):
                st.error("Der Domain-Teil der E-Mail-Adresse enthält ungültige Zeichen", icon="📧")
                return False
        # Wenn alle Prüfungen bestanden sind, ist die E-Mail gültig
        return True
    def passwort_check(passwort):
        if len(passwort) < 8:
            st.error("Das Passwort muss mindestens 8 Zeichen lang sein", icon="🔑")
            return False
        else: return True
    # Validierung der Eingaben
    def validate_input():
        if not matrikelnummer:
            st.error("Bitte geben eine Valide und erlaubte Matrikelnummer an", icon="📟")
            return False
        elif not vorname:
            st.error("Bitte geben Sie einen Vornamen an", icon="🧑")
            return False
        elif not nachname:
            st.error("Bitte geben Sie einen Nachnamen an", icon="🧑")
            return False
        elif not email:
            st.error("Bitte geben Sie eine E-Mail-Adresse an", icon="📧")
            return False
        elif not is_valid_email(email):
            return False
        elif not passwort:
            st.error("Bitte geben Sie ein Passwort an", icon="🔑")
            return False
        elif not passwort_check(passwort):
            return False
        else:
            return True
    if submit_button:
        if validate_input():
            # Benutzer hinzufügen
            if add_user_in_admin(matrikelnummer, vorname, nachname, email, passwort, is_user_admin) == True:
                st.toast(f"{vorname} {nachname} erfolgreich registriert", icon='🎉')
                st.rerun()  # Seite aktualisieren, um das Formular zurückzusetzen

@st.dialog("Achtung!")
def delete_user_warning(matrikelnummern_delete_input):
    with st.container():
        st.write(f"Hier mit löschen sie den User, mit der Matrikelnummer: {matrikelnummern_delete_input}, und alle Lern Fortschritte unwiederruflich!")
        st.write("Sind Sie sie WIRKLICH, dass Sie diesen User löschen möchten?")
        if st.button("JA, ich bin mir sicher", type="secondary"):
            st.toast(f"User, mit der Matrikelnummer: {matrikelnummern_delete_input}, wurde gelöscht", icon="🗑️")
            delete_user_completly(matrikelnummern_delete_input)
            st.rerun()  #Seite aktualisieren, um löschen in User Datenbank zu akuallisieren
        if st.button("NEIN", type="primary"):
            st.toast(f"User, mit der Matrikelnummer: {matrikelnummern_delete_input}, wurde nicht gelöscht", icon="❌")
            st.rerun()  # Seite aktualisieren, um dialog zu schließen  

@st.dialog("Achtung!")
def delete_warning_lecture(lecture_titel):
    with st.container():
        st.write(f"Möchten Sie wirklich {lecture_titel} und alle dahin stehende fragen unwiederruflich löschen?")
        st.write("Sind Sie sich sicher?")
        if st.button("JA, ich bin mir sicher", type="secondary"):
            st.toast(f"Vorlesung {lecture_titel} wurde gelöscht", icon="🗑️")
            delete_lecture(lecture_titel)
            st.rerun()  # Seite aktualisieren, um löschen in Vorlesung Datenbank zu akuallisieren
        if st.button("NEIN", type="primary"):
            st.toast(f"Vorlesung {lecture_titel} wurde nicht gelöscht", icon="❌")
            st.rerun()  # Seite aktualisieren, um dialog zu schließen
        
@st.dialog("Achtung!")
def delete_question_mtl(question_id):
    with st.container():
        st.write(f"Möchten Sie wirklich die Frage mit der ID: {question_id} entgültig löschen?")
        st.write("Sind Sie sich sicher?")
        if st.button("JA, ich bin mir sicher", type="secondary"):
            delete_mtl_question(question_id)
            st.toast(f"Frage mit der ID: {question_id} wurde gelöscht", icon="🗑️")
            st.rerun() # Seite aktualisieren, um löschen in Multiple Choice Fragen Datenbank zu akuallisieren
        if st.button("NEIN", type="primary"):
            st.toast(f"Frage mit der ID: {question_id} wurde nicht gelöscht", icon="❌")
            st.rerun() # Seite aktualisieren, um dialog zu schließen



# --- User Verwaltung ---
st.header("User Verwaltung")
user_1, user_2, user_3, user_4 = st.tabs(["User suchen", "User hinzufügen", "User bearbeiten", "Erlaubte Matrikelnummer Verwahltung"])
with user_1:
    user_data = get_all_users_info()
    user_df = pd.DataFrame([user.dict() for user in user_data], 
        columns=['matrikelnummern', 'vorname', 'nachname', 'email', 'passwort', 'admin'],
        index=np.arange(1, len(user_data)+1)
    )
    st.dataframe(user_df, use_container_width=True, height=400)
with user_2:
    registration_page()
with user_3:
    user_data = get_all_users_info()
    user_df = pd.DataFrame([user.dict() for user in user_data], 
        columns=['matrikelnummern', 'vorname', 'nachname', 'email', 'passwort', 'admin'],
        index=np.arange(1, len(user_data)+1)
    )
    edited_df = st.data_editor(user_df, use_container_width=True, height=400)
    for index, row in edited_df.iterrows():
        update_all_users_info(row['matrikelnummern'], row['vorname'], row['nachname'], row['email'], row['passwort'], row['admin'])
    # Löschen von Usern
    with st.form(key='User_löschen', clear_on_submit=True):
        def validate_delete_user_form():
            if not matrikelnummern_delete_input:
                st.toast("Bitte geben Sie eine Matrikelnummer an", icon="❌")
                return False
            else:
                all_user = get_registered_user_ids()
                if matrikelnummern_delete_input in all_user:
                    return True
                else:
                    st.toast("Matrikelnummer existiert nicht", icon="❌")
                    return False
        st.subheader("User löschen")
        matrikelnummern_delete_input = st.text_input("Matrikelnummer", placeholder="z.B. 30400")
        lösch_button = st.form_submit_button("User Löschen", type="primary")
        if lösch_button:
            if validate_delete_user_form():
                delete_user_warning(matrikelnummern_delete_input)
with user_4:
    with st.container(height=400, border=True):
        mat1, mat2 = st.columns(2)
        # Anzeige der unregistrierten Matrikelnummern
        with mat1:
            st.subheader("Unregistrierte Matrikelnummern")
            matrikelnummern_liste = get_unregistered_matrikelnummern()
            data_df = pd.DataFrame({
                "Unregistrierte Matrikelnummern": matrikelnummern_liste
            })
            
            # Darstellung der Tabelle und Lösch-Button hinzufügen
            for idx, row in data_df.iterrows():
                col1, col2 = st.columns([1, 1], gap="small", vertical_alignment="center")
                col1.write(row["Unregistrierte Matrikelnummern"])
                if col2.button("Löschen", key=f"delete_{row['Unregistrierte Matrikelnummern']}", use_container_width=False):
                    delete_erlaubte_matrikelnummer(row["Unregistrierte Matrikelnummern"])
                    st.rerun()  # Seite aktualisieren, um die geänderte Tabelle zu laden
        with mat2:
            st.subheader("Matrikelnummern Registrierung erlauben", divider="red")
            with st.form(key='Erlaubte Matrikelnummern', clear_on_submit=True):
                matrikelnummern = st.text_input("Matrikelnummer", placeholder="z.B. 30400")
                submit_button = st.form_submit_button("Erlauben", type="primary")
            if submit_button:
                add_unregistered_matrikelnummern(matrikelnummern)
                st.rerun()  # Seite aktualisieren, um die geänderte Tabelle zu laden
                

# --- Vorlesung Verwaltung ---
st.header("Vorlesungen")
lecture_1, lecture_2, lecture_3 = st.tabs(["Suchen", "Hinzufügen", " Bearbeiten"])
with lecture_1:
    with st.container():
        lecture_data = get_all_lectures()
        lecture_df = pd.DataFrame([lecture.dict() for lecture in lecture_data],
            columns=['id', 'title', 'description']
        )
        st.dataframe(lecture_df, hide_index=True, use_container_width=True, height=400)
with lecture_2:
    with st.form("add_lecture", clear_on_submit=True):
        title = st.text_input("Titel")
        description = st.text_area("Beschreibung")
        lecture_submit = st.form_submit_button("Hinzufügen")
        def validate_lecture_input():
            if not title:
                st.toast("Bitte geben Sie einen Titel ein", icon="❌")
                return False
            elif not description:
                st.toast("Bitte geben Sie eine Beschreibung ein", icon="❌")
                return False
            else:
                return True
        if lecture_submit:
            if validate_lecture_input():
                add_lecture(title, description)
                st.toast("Vorlesung hinzugefügt", icon='🎉')
                st.rerun()
with lecture_3:
    lecture_data = get_all_lectures()
    lecture_df = pd.DataFrame([lecture.dict() for lecture in lecture_data],
        columns=['id', 'title', 'description'] 
    )
    edited_df = st.data_editor(lecture_df, hide_index=True, use_container_width=True, height=400)
    for index, row in edited_df.iterrows():
        update_lecture(row['id'], row['title'], row['description'])
    # Löschen von Vorlesungen und aller Fragen in der Vorlesung
    with st.form(key='Vorlesung_löschen', clear_on_submit=True):
        st.subheader("User löschen")
        lecture_delete_selection = st.selectbox("Vorlesung", [lecture.title for lecture in get_all_lectures()], index=None, placeholder="Wählen Sie eine Vorlesung aus")
        if st.form_submit_button("Vorlesung löschen", type="primary"):
            # Übperrüfen ob eine Vorlesung ausgewählt wurde oder ob select box leer ist
            if not lecture_delete_selection:
                st.toast("Bitte wählen Sie eine Vorlesung aus", icon="❌")
            else:
                delete_warning_lecture(lecture_delete_selection)


#Multiple Choice Fragen
st.header("Multiple Choice Fragen")
mtl_1, mtl_2, mtl_3 = st.tabs(["Suchen", "Hinzufügen", " Bearbeiten"])
with mtl_1:
    question_data = get_all_mtl_questions()
    question_df = pd.DataFrame([question.dict() for question in question_data],
        columns=['id', 'lecture_id', 'question_text', 'options_1', 'options_2', 'options_3', 'options_4', 'answer']
    )
    st.dataframe(question_df, hide_index=True, use_container_width=True, height=400)
with mtl_2:  # Fragen können hier hinzugefügt werden
    with st.container(border=True):
        # Initialisiere die Formulardaten, falls sie nicht existieren
        if "form_data" not in st.session_state or not isinstance(st.session_state.form_data, dict):
            st.session_state.form_data = {
                "frage": "",
                "options": ["", ""],  # Mindestens 2 leere Felder
                "lecture_index": None,  # Index für die Lecture-Selectbox
                "answer_index": None,  # Index für die Antwort-Selectbox
                "valid": False,  # Status des Formulars
            }

        # Initialisiere Toast-Status
        if "toast_message" not in st.session_state:
            st.session_state.toast_message = None

        # Funktion zum Zurücksetzen der Formulardaten
        def reset_form():
            st.session_state.form_data = {
                "frage": "",
                "options": ["", ""],
                "lecture_index": None,
                "answer_index": None,
                "valid": False,
            }

        # Funktion zum Hinzufügen einer neuen Option
        def add_option():
            if len(st.session_state.form_data["options"]) < 4:
                st.session_state.form_data["options"].append("")
            else:
                st.toast("Maximal 4 Antwortmöglichkeiten erlaubt", icon="⚠️")

        # Funktion zum Entfernen einer Option
        def remove_option(index):
            if len(st.session_state.form_data["options"]) > 2:
                st.session_state.form_data["options"].pop(index)
            else:
                st.toast("Mindestens 2 Antwortmöglichkeiten erforderlich", icon="⚠️")

        # Formular für die Frageeingabe
        st.subheader("Frage hinzufügen")

        # Dynamische Auswahl der Vorlesung
        all_lectures = [lecture.title for lecture in get_all_lectures()]
        lecture_titel = st.selectbox(
            "Vorlesung",
            options=all_lectures,
            index=st.session_state.form_data.get("lecture_index", 0),
            placeholder="Wählen Sie eine Vorlesung aus",
        )
        st.session_state.form_data["lecture_index"] = (
            None if lecture_titel is None else all_lectures.index(lecture_titel)
        )

        # Eingabefeld für die Frage
        st.session_state.form_data["frage"] = st.text_input(
            "Frage:", value=st.session_state.form_data["frage"]
        )

        # Dynamische Antwortmöglichkeiten
        st.subheader("Antwortmöglichkeiten")
        for i, option in enumerate(st.session_state.form_data["options"]):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.session_state.form_data["options"][i] = st.text_input(
                    f"Option {i + 1}:", value=option, key=f"option_{i}"
                )
            with col2:
                if len(st.session_state.form_data["options"]) > 2:
                    if st.button(f"❌ Entfernen Option {i + 1}", key=f"remove_option_{i}"):
                        remove_option(i)
                        st.rerun()

        # Button zum Hinzufügen neuer Antwortmöglichkeiten
        if len(st.session_state.form_data["options"]) < 4:
            if st.button("Option hinzufügen"):
                add_option()
                st.rerun()

        # Dynamische Antwort-Selectbox
        answer_options = [f"Option {i + 1}" for i in range(len(st.session_state.form_data["options"]))]
        antwort_index = st.selectbox(
            "Antwort",
            options=answer_options,
            index=st.session_state.form_data.get("answer_index", 0),
            placeholder="Wählen Sie die richtige Antwort aus",
        )
        st.session_state.form_data["answer_index"] = (
            None if antwort_index is None else answer_options.index(antwort_index)
        )

        # Formular-Submit-Button
        if st.button("Frage hinzufügen", type="primary"):
            # Validierungsfunktion
            def validate_input():
                if st.session_state.form_data["lecture_index"] is None:
                    st.toast("Bitte wählen Sie eine Vorlesung aus", icon="❌")
                    return False
                elif not st.session_state.form_data["frage"]:
                    st.toast("Bitte geben Sie eine Frage ein", icon="❌")
                    return False
                elif len(st.session_state.form_data["options"]) < 2:
                    st.toast("Bitte geben Sie mindestens zwei Antwortmöglichkeiten ein", icon="❌")
                    return False
                elif st.session_state.form_data["answer_index"] is None:
                    st.toast("Bitte wählen Sie eine gültige Antwort aus", icon="❌")
                    return False
                return True

            if validate_input():
                # Optionen normalisieren
                options = st.session_state.form_data["options"] + [""] * (
                    4 - len(st.session_state.form_data["options"])
                )
                add_mtl_question(
                    all_lectures[st.session_state.form_data["lecture_index"]],
                    st.session_state.form_data["frage"],
                    options[0],
                    options[1],
                    options[2],
                    options[3],
                    f"Option {st.session_state.form_data['answer_index'] + 1}",
                )
                # Setze die Toast-Message in den Session-State
                st.session_state.toast_message = "Frage hinzugefügt! 🎉"
                reset_form()
                st.rerun()

        # Zeige den Toast nach dem Neuladen
        if st.session_state.toast_message:
            st.toast(st.session_state.toast_message, icon="✅")
            # Setze die Nachricht zurück, um sie nur einmal anzuzeigen
            st.session_state.toast_message = None

with mtl_3:
    question_data = get_all_mtl_questions()
    question_df = pd.DataFrame([question.dict() for question in question_data],
        columns=['id', 'lecture_id', 'question_text', 'options_1', 'options_2', 'options_3', 'options_4', 'answer']
    )
     # Zeige den Editor für die Fragen
    edited_df = st.data_editor(question_df, hide_index=True, use_container_width=True, height=400)
    
    # Aktualisiere die Fragen basierend auf den Änderungen im Editor
    for index, row in edited_df.iterrows():
        update_mtl_question(
            question_id=row['id'], 
            lecture_id=row['lecture_id'], 
            question_text=row['question_text'], 
            options_1=row['options_1'], 
            options_2=row['options_2'], 
            options_3=row['options_3'], 
            options_4=row['options_4'], 
            answer=row['answer']
        )
    # Löschen von Multiple-Choice-Fragen
    with st.form(key='MTL_löschen', clear_on_submit=True):
        st.subheader("Multiple Choice Frage löschen")
        question_id = st.text_input("Frage ID", placeholder="Nummer aus der ID-Spalte z.B. 1 oder 43")
        delete_button = st.form_submit_button("Frage löschen", type="primary")
        
        if delete_button:
            # Überprüfe, ob eine Frage-ID eingegeben wurde oder das Feld leer ist
            if not question_id:
                st.toast("Bitte geben Sie eine gültige Fragen-ID ein", icon="❌")
            else:
                delete_question_mtl(question_id)

st.divider()
with st.popover("Alle Datenbank", icon="🗄"):
    with st.container(height=500):
        st.header("Alle Datenbank")
        st.subheader("Erlaubte Matrikelnummern")
        st.subheader("User")
        st.subheader("Lecture")
        st.subheader("MTL Question")
        st.subheader("User Progress")

