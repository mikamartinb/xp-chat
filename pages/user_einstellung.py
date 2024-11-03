import streamlit as st
from SQLmodule_commands import get_user_full_name

st.set_page_config(
    page_title="Einstellung",
    page_icon="⚙️",
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


# --- Page Content ---
col1, col2 = st.columns(2, gap="small", vertical_alignment="center")
with col1:
    st.image("images/User_Profile_image.png", width=230)

with col2:
    vor_und_nachname = get_user_full_name(st.session_state.matrikelnummer)
    st.title(f"{vor_und_nachname}", anchor=False)
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")

st.header("", divider="red")
st.write("## Einstellungen")