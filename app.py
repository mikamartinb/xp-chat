import streamlit as st
from PageRenderer import PageRenderer
import warnings

warnings.filterwarnings("ignore", message="Ignoring wrong pointing object")

# Initialisiere den PageRenderer
renderer = PageRenderer()

# Session State initialisieren
if "pages" not in st.session_state:
    st.session_state.pages = []

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Home"

if "show_add_page_dialog" not in st.session_state:
    st.session_state.show_add_page_dialog = False

if "policy_accepted" not in st.session_state:
    st.session_state.policy_accepted = False

# Maximale Anzahl von Seiten
MAX_PAGES = 6

# Policy Notice Dialog
@st.dialog("Policy Notice")
def policy_notice():
    st.markdown("""
    ### Welcome to the Application
    Please review and accept our policy to continue:

    - By using this application, you agree to our terms and conditions.
    - Ensure you follow all usage guidelines provided.
    """)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Accept"):
            st.session_state.policy_accepted = True
            st.rerun()
    with col2:
        if st.button("Decline"):
            st.stop()

if not st.session_state.policy_accepted:
    policy_notice()
    
# Sidebar
st.sidebar.header("🧭 Navigator")

# Home-Button anzeigen
if st.sidebar.button("Home", key="home_button"):
    st.session_state.selected_page = "Home"

# Abschnitt für die erstellten Klassen
if st.session_state.pages:
    st.sidebar.markdown("---")
    st.sidebar.header("📓 Your Classes")

    # Buttons für vorhandene Klassen
    for page in st.session_state.pages:
        if st.sidebar.button(page, key=page):
            st.session_state.selected_page = page

# Button für neues Seitenformular an das Ende der Sidebar verschieben
st.sidebar.markdown("---")
if len(st.session_state.pages) < MAX_PAGES:
    if st.sidebar.button("Add a new Class", key="add_page"):
        st.session_state.show_add_page_dialog = True
else:
    st.sidebar.write("⚠️ Maximum number of pages reached!")

# Dialog anzeigen, um einen neuen Seitennamen einzugeben
@st.dialog("Add a New Class")
def add_new_class():
    new_page_name = st.text_input("Insert Class Name")

    if st.button("Add", use_container_width=True):
        if new_page_name:
            st.session_state.pages.append(new_page_name)
            st.session_state.selected_page = new_page_name
            st.session_state.show_add_page_dialog = False
            st.rerun()

if st.session_state.show_add_page_dialog:
    add_new_class()

# Inhalte der ausgewählten Seite anzeigen
renderer.render(st.session_state.selected_page)