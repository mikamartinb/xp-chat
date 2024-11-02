import streamlit as st
import streamlit_authenticator as stauth
import requests
from SQLmodule_commands import(
    add_user, login_check, 
    create_tables, is_user_admin
)


st.set_page_config(
    page_title="Login/Registrierung",
    page_icon="🔑",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://www.google.com',
        'Report a bug': "https://www.google.com",
        'About': "# Viel Spaß! Beim Lernen für die WI-Prüfung"
    }
)

create_tables()  # Erstellt die Tabellen in der Datenbank und checkt, ob sie schon existieren
#create_admin_user()  # Einmalig ausführen, um einen Admin zu erstellen

# Initialisiere Session-Variablen nur, wenn sie noch nicht gesetzt sind
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "page" not in st.session_state:
    st.session_state.page = "login"  # Standardmäßig auf die Login-Seite setzen

def registration_page():
    # Formular für die Registrierung
    with st.form(key='Registrierung'):
        matrikelnummer = st.text_input("Matrikelnummer", placeholder="Die Matrikelnummer muss zugelassen sein")
        vorname = st.text_input("Vorname", placeholder="z.B. Max")
        nachname = st.text_input("Nachname", placeholder="z.B. Mustermann")
        email = st.text_input("E-Mail", placeholder="z.B. max-mustermann@gmail.com")
        passwort = st.text_input("Passwort", placeholder="z.B. Max!1234", type="password")
        passwort_wiederholung = st.text_input("Passwort wiederholen", placeholder="Hier bitte das gleiche Passwort", type="password")
        checkbox = st.checkbox("Ich stimme den [Nutzungsbedingungen](pages/nutzungsbedingung) und den [Datenschutzrichtlinien](pages/datenschutz.py) zu")
        submit_button = st.form_submit_button("Registrieren", type="primary") 
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
        elif not passwort_wiederholung:
            st.error("Bitte wiederholen Sie das Passwort", icon="🔑")
            return False
        elif passwort != passwort_wiederholung:
            st.error("Die Passwörter stimmen nicht überein", icon="🔑")
            return False
        elif not checkbox:
            st.error("Bitte stimmen Sie den Nutzungsbedingungen und Datenschutzrichtlinien zu", icon="📜")
            return False
        else:
            return True
    if submit_button:
        if validate_input():
            # Benutzer hinzufügen
            if add_user(matrikelnummer, vorname, nachname, email, passwort, False) == True:
                st.toast(f"{vorname} {nachname} erfolgreich registriert", icon='🎉')
                st.session_state.matrikelnummer = matrikelnummern


# Funktion für die Benutzerregistrierung
def user_registration():
    st.header("Registrieren")
    try:
        if registration_page():
            st.session_state.logged_in = True
            st.switch_page("pages/home.py")
        st.divider()
        st.button("Zurück zum Login", on_click=go_to_login)
    except Exception as e:
        st.error(f"Fehler: {e}")

# Funktion für das Login-Fenster
def login_page():
    try:    
        st.header("Login")
        with st.form(key='Login'):
            matrikelnummern = st.text_input("Matrikelnummer", placeholder="z.B. 30400")
            passwort = st.text_input("Passwort", placeholder="z.B. Max!1234", type="password")
            if st.form_submit_button("Login", type="primary"):
                if login_check(matrikelnummern, passwort) == True:
                    st.session_state.logged_in = True
                    st.session_state.is_admin = is_user_admin(matrikelnummern)  # Admin-Status speichern
                    if st.session_state.is_admin:
                        st.toast("Eingeloggt als Admin!", icon='🎉')
                    else:
                        st.toast("Eingeloggt!", icon='🎉')
                    st.session_state.matrikelnummer = matrikelnummern
                    st.switch_page("pages/home.py")  # Weiterleitung zur Home-Seite
        st.divider()
        st.button("Registrieren", type="secondary", on_click=go_to_register)
        
    except Exception as e:
        st.error(f"Fehler: {e}")

# Funktion für das Registrier-Fenster
def register_page():
    user_registration()

def go_to_register():
    st.session_state.page = "register"

def go_to_login():
    st.session_state.page = "login"

# Anzeige des aktuellen Fensters basierend auf dem Login-Status und Status
if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "register":
        register_page()
else:
    st.switch_page("pages/home.py")  # Falls eingeloggt, automatisch zur Home-Seite wechseln
