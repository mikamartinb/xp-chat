import streamlit as st
from PageRenderer import PageRenderer
import warnings

warnings.filterwarnings("ignore", message="Ignoring wrong pointing object")

# Initialisiere den PageRenderer
renderer = PageRenderer()

# Session State initialisieren
if "pages" not in st.session_state:
    st.session_state.pages = ["Home"]

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Home"

if "show_add_page_form" not in st.session_state:
    st.session_state.show_add_page_form = False

# Maximale Anzahl von Seiten
MAX_PAGES = 6

# Sidebar
st.sidebar.title("Navigator")

# Aktuelle Seite auswählen
for page in st.session_state.pages:
    if st.sidebar.button(page, key=page):
        st.session_state.selected_page = page

# Button für neues Seitenformular
if len(st.session_state.pages) < MAX_PAGES:
    if st.sidebar.button("Add a new Class", key="add_page"):
        st.session_state.show_add_page_form = True
else:
    st.sidebar.write("⚠️ Maximale Seitenanzahl erreicht!")

# Formular anzeigen, um einen neuen Seitennamen einzugeben
if st.session_state.show_add_page_form:
    with st.sidebar.form("add_page_form"):
        new_page_name = st.text_input("Name der neuen Seite")
        submit = st.form_submit_button("Hinzufügen")
        cancel = st.form_submit_button("Abbrechen")

        if submit and new_page_name:
            st.session_state.pages.append(new_page_name)
            st.session_state.selected_page = new_page_name
            st.session_state.show_add_page_form = False
            st.rerun()

        if cancel:
            st.session_state.show_add_page_form = False

# Inhalte der ausgewählten Seite anzeigen
renderer.render(st.session_state.selected_page)
