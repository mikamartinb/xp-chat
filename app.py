import json
from model_utils import create_vector_store
from exam_utils import create_exam_document
import streamlit as st
import os
from datetime import datetime
import io, zipfile
from time import sleep as time
import shutil

# Constants
MAX_PAGES = 6  # Maximum number of pages
CLASSES_DIR = "Classes"

# Ensure the "Classes" folder exists
if not os.path.exists(CLASSES_DIR):
    os.mkdir(CLASSES_DIR)

# Global variables
if "all_pages" not in st.session_state:
    st.session_state.all_pages = os.listdir(CLASSES_DIR)

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

def reload_pages():
    st.session_state.all_pages = os.listdir(CLASSES_DIR)

def reload_exams(class_name):
    CurrentClassDIR = os.path.join(CLASSES_DIR, class_name)
    st.session_state.all_exams_in_class = os.listdir(CurrentClassDIR)

@st.dialog("Delete Class", width="small")
def delete_page(page_name):
    """Deletes a class and removes it from the list."""
    page_path = os.path.join(CLASSES_DIR, page_name)
    if os.path.exists(page_path):
        st.write(f"Are you sure you want to delete the Class {page_name}...?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cancel", key="delete_cancel", type="primary"):
                st.rerun()
        with col2:
            if st.button("yes, I am sure", key="delete_confirm"):
                shutil.rmtree(page_path)
                st.session_state.all_pages.remove(page_name)
                st.success(f"Class {page_name} deleted successfully!")
                st.rerun()

# Home page
def home_page():
    st.image("public/XP-CHAT.png", use_container_width=True)
    st.title("Welcome to the Class Manager!")
    if st.button("Create new Class", icon="➕", key="new_class_button", use_container_width=True, type="primary"):
        newClassForm()
    st.write("### Classes:")
    with st.container(border=False):
        for page in st.session_state.all_pages:
            with st.container(border=True):
                if page == ".DS_Store":
                    continue
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.subheader(f":green[{page}]")
                # Offnet die seite mit dem Klassen Namen
                with col2:
                    if st.button(f"Open **{page}** ➡️", key=f"Home_{page}_button", type="primary", use_container_width=True):
                        st.session_state.current_page = page
                with col3:
                    if st.button("Delete", key=f"delete_{page}"):
                        delete_page(page)


# Class page
def class_page(class_name):
    reload_exams(class_name)
    CurrentClassDIR = os.path.join(CLASSES_DIR, class_name)

    if "all_exams_in_class" not in st.session_state:
        st.session_state.all_exams_in_class = os.listdir(CurrentClassDIR)

    # Create new exam folder and redirect to Exam Form
    @st.fragment() 
    def create_new_exam(new_exam_name):
        """Creates a new exam in the specified class."""
        new_exam_DIR = os.path.join(CurrentClassDIR, new_exam_name)
        if os.path.exists(new_exam_DIR):  # statt os.path.exists(new_exam_name)
            st.toast(f"Exam :green[{new_exam_name}] already exists!")
            return False
        else:
            NewExam = newExamName(new_exam_DIR, new_exam_name)
            if NewExam:
                st.rerun()  # Schließt das Dialog und aktualisiert die Liste
            return False
        


    # Create new exam name
    @st.dialog("Create a new Exam", width="large")
    def newExamName(new_exam_DIR, new_exam_name):
        all_input_pdf_files = []
        uploaded_files = st.file_uploader(
                "Upload one or more PDFs before generation", 
                type="pdf", 
                key=f"uploader_{new_exam_name}",
                accept_multiple_files=True
            )
        with st.form(key="new_exam_form", clear_on_submit=True):
            st.markdown("\n")
            st.subheader("General Information", divider="gray")
            exam_topic = st.text_input(label="Exam Topic", placeholder="Exam Topic")
            university = st.text_input(label="University", placeholder="University")
            date = st.date_input(label="Date of the exam", value="today", format="DD.MM.YYYY")
            c1, c2 = st.columns(2)
            with c1:
                semester = st.selectbox(label="Semester", options=["Wintersemester 2024/2025", "Sommersemester 2025", "Wintersemester 2025/2026", "Sommersemester 2026"], placeholder="Choose a Semester")
            with c2:
                prof_title = st.selectbox(label="Title", options=["B. A.", "B. Sc.", "M. A.", "M. Sc.", "Dr.", "Prof.", "Prof. Dr.", "Prof. Dr. Dr."], placeholder="Choose Title", index=None)
            professor = st.text_input(label="Examiner", placeholder="Max Mustermann")
                
            st.markdown("\n")
            st.subheader("Task Specification", divider="gray")
            exam_focus = st.text_area(label="Exam Focus", placeholder="Exam Focus", height=100)
            irr_topics = st.text_area(label="Irrelevant Topics", placeholder="Irrelevant Topics", height=100)
            c1, c2, c3 = st.columns(3)
            with c1:
                num_tasks = st.number_input(label="Number of Questions", min_value=1, max_value=40, placeholder="Number of Tasks")
            with c2:
                num_points = st.number_input(label="Points per Questions", min_value=1, max_value=100, placeholder="Points per Task")
            with c3:
                st.markdown("")
                st.markdown("")
                multi_select = st.toggle("Multi Select")
            

            submit_form = st.form_submit_button(
                "Generate",
                use_container_width=True,
                type="primary",
                disabled=(not uploaded_files)
            )

            if submit_form:
                with st.spinner("Creating exam..."):
                    exam_data = {
                        "exam_topic": exam_topic,
                        "university": university,
                        "date": date.strftime("%d.%m.%Y"),
                        "module": class_name,
                        "prof_title": prof_title,
                        "semester": semester,
                        "professor": professor,
                        "exam_focus": exam_focus,
                        "irr_topics": irr_topics,
                        "num_tasks": num_tasks,
                        "num_points": num_points,
                        "multi_select": multi_select
                    }
                    # Create exam folder
                    os.mkdir(new_exam_DIR)

                    # Save exam data to JSON file
                    exam_json_file_DIR = os.path.join(new_exam_DIR, f"{new_exam_name}.json")
                    with open(exam_json_file_DIR, "w") as json_file:
                        json.dump(exam_data, json_file, indent=4)
                    
                    # Save uploaded PDFs to input directory and store them in a Vector Store
                    pdf_input_DIR = os.path.join(new_exam_DIR, "pdf_input")
                    os.mkdir(pdf_input_DIR)
                    for uploaded_file in uploaded_files:
                        current_uploaded_pdf = os.path.join(pdf_input_DIR, uploaded_file.name)
                        with open(current_uploaded_pdf, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        all_input_pdf_files.append(current_uploaded_pdf)
                    vector_store_DIR = os.path.join(new_exam_DIR, "vector_store")
                    vector_store = create_vector_store(all_input_pdf_files, vector_store_DIR)

                    # Create output directory
                    output_DIR = os.path.join(new_exam_DIR, "output")
                    os.mkdir(output_DIR)

                    # Create exam documents
                    if vector_store:
                        # hier muss die Logik die Exams zu erstellen 
                        createExam = create_exam_document(exam_json_file_DIR, vector_store, class_name, output_DIR)
                        if createExam:
                            reload_exams(class_name)
                            st.rerun()

    # Delete Exam
    @st.dialog("Delete Exam", width="small")
    def delete_exam(exam_name):
        """Deletes an exam and removes it from the list."""
        exam_path = os.path.join(CurrentClassDIR, exam_name)
        st.write(f"Are you sure you want to delete the Exam {exam_name}...")
        #Check if Exam folder exits
        if os.path.exists(exam_path):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Cancel", key="delete_exam_cancel", type="primary"):
                    st.rerun()
            
            with col2:
                if st.button("yes, I am sure", key="delete_exam_confirm"):
                    shutil.rmtree(exam_path)
                    st.session_state.all_exams_in_class.remove(exam_name)
                    st.rerun()
        else:
            st.rerun()

    #Create new Exam from Templte 
    @st.fragment()
    def create_new_exam_from_template(new_exam_input, exam_data, old_exam_DIR):
        """Creates a new exam from a template."""
        new_exam_DIR = os.path.join(CurrentClassDIR, new_exam_input)
        if os.path.exists(new_exam_input):
            st.toast(f"Exam :green[{new_exam_input}] already exists!")
            return False
        else:
            # Create exam folder
            os.mkdir(new_exam_DIR)

            # Save exam data to JSON file
            exam_json_file_DIR = os.path.join(new_exam_DIR, f"{new_exam_input}.json")
            with open(exam_json_file_DIR, "w") as json_file:
                json.dump(exam_data, json_file, indent=4)
            
            # Copie Input PDF from old Exam to new Exam
            new_exam_input_PDF_DIR = os.path.join(new_exam_DIR, "pdf_input")
            os.mkdir(new_exam_input_PDF_DIR)
            old_exam_input_PDF_DIR = os.path.join(old_exam_DIR, "pdf_input")
            # Copy all PDFs from old exam to new exam
            for file in os.listdir(old_exam_input_PDF_DIR):
                shutil.copy(os.path.join(old_exam_input_PDF_DIR, file), new_exam_input_PDF_DIR)

            # Create output directory
            output_DIR = os.path.join(new_exam_DIR, "output")
            os.mkdir(output_DIR)

            # Gather all PDFs from new exam folder and build a vector store
            pdf_input_DIR = os.path.join(new_exam_DIR, "pdf_input")
            all_input_pdf_files = []
            for file in os.listdir(pdf_input_DIR):
                all_input_pdf_files.append(os.path.join(pdf_input_DIR, file))
            vector_store_DIR = os.path.join(new_exam_DIR, "vector_store")
            vector_store = create_vector_store(all_input_pdf_files, vector_store_DIR)

            # Use the vector store object, not the string path
            createExam = create_exam_document(exam_json_file_DIR, vector_store, class_name, output_DIR)
            if createExam:
                st.rerun()
            else:
                return False
            

    
    # Delete Exam Button
    @st.fragment()
    def delete_exam_button(exam_name):
        if st.button("Delete", key=f"delete_{exam_name}", help="Delete this Exam", use_container_width=True):
            delete_exam(exam_name)

    # Page Information
    st.title(f"Class: :green[{class_name}]")
    with st.form(key="new_exam_name_form", clear_on_submit=True):
        new_exam_name = st.text_input("Name of new Exam", placeholder="Name of new Exam")
        submit = st.form_submit_button("Create a new Exam")
        if submit and new_exam_name:
            create_new_exam(new_exam_name)
            reload_exams(class_name)
    
    #List all Exams in the Class
    st.write("### Exams:")
    for exam in st.session_state.all_exams_in_class:
        # CSS für spezifisches stMarkdownContainer im Expander
        st.markdown("""
            <style>
                /* Ziel: Nur den stMarkdownContainer innerhalb des Expanders anpassen */
                [data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] p {
                    font-size: 25px !important; /* Schriftgröße ändern */
                    font-weight: bold !important; /* Fettgedruckt */
                    border: 2px solid #0FA37F !important; /* Rahmen */
                    border-radius: 5px !important; /* Eckenradius */
                    color: #F0F0F0 !important; /* Textfarbe */
                    padding-top: 2px !important; /* Innenabstand */
                    padding-bottom: 2px !important; /* Innenabstand */
                    padding-left: 10px !important; /* Innenabstand */
                    padding-right: 10px !important; /* Innenabstand */
                    background-color: #0FA37F !important; /* Hintergrundfarbe */
                }
            </style>
            """, unsafe_allow_html=True)
        with st.expander(f"**{exam}**", expanded=False):
            current_Exam_DIR = os.path.join(CurrentClassDIR, exam)

            # Download all exams in DOCX and PDF in zip file
            def download_all_exams():
                pdf_files_DIR = os.path.join(current_Exam_DIR, "output", "PDF")
                docx_files_DIR = os.path.join(current_Exam_DIR, "output", "DOCX")
                buffer = io.BytesIO()
                with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for file in os.listdir(pdf_files_DIR):
                        pdf_path = os.path.join(pdf_files_DIR, file)
                        zipf.write(pdf_path, os.path.join("PDF", file))
                    for file in os.listdir(docx_files_DIR):
                        docx_path = os.path.join(docx_files_DIR, file)
                        zipf.write(docx_path, os.path.join("DOCX", file))
                buffer.seek(0)
                return buffer.getvalue()

            col1, col2 = st.columns(2, gap="small")
            with col1:
                if st.download_button(
                label=f"Download {exam}",
                data=download_all_exams(),
                file_name=f"{exam}.zip",
                key=f"{exam}_downloadButton",
                type="primary",
                help="Download all exams in DOCX and PDF in zip file",
                use_container_width=True
                ):
                    st.toast(f"Downloading... :green[{exam}.zip]", icon="📥")
            with col2:
                delete_exam_button(exam)

            #Edit the Values in teh Json File
            st.subheader("Use as template to create a new Exam: ")
            with st.form(key=f"edit_{exam}_form", clear_on_submit=True):
                new_exam_input = st.text_input("Name of new Exam", key=f"edit_{exam}_input", placeholder="Name of new Exam")
                current_json_file = open(os.path.join(current_Exam_DIR, f"{exam}.json"))
                tamplate_exam_data = json.load(current_json_file)
                st.subheader("General Information", divider="gray")
                exam_topic = st.text_input(label="Exam Topic", value=tamplate_exam_data["exam_topic"])
                university = st.text_input(label="University", value=tamplate_exam_data["university"])
                date = st.date_input(label="Date of the exam", value=datetime.strptime(tamplate_exam_data["date"], "%d.%m.%Y"), format="DD.MM.YYYY")
                c1, c2 = st.columns(2)
                with c1:
                    semesters = ["Wintersemester 2024/2025", "Sommersemester 2025", "Wintersemester 2025/2026", "Sommersemester 2026"]
                    try:
                        semester_index = semesters.index(tamplate_exam_data["semester"])
                    except ValueError:
                        semester_index = 0
                    semester = st.selectbox("Semester", semesters, index=semester_index)
                with c2:
                    titles = ["B. A.", "B. Sc.", "M. A.", "M. Sc.", "Dr.", "Prof.", "Prof. Dr.", "Prof. Dr. Dr."]
                    try:
                        title_index = titles.index(tamplate_exam_data["prof_title"])
                    except ValueError:
                        title_index = 0
                    prof_title = st.selectbox("Title", titles, index=title_index)
                professor = st.text_input(label="Examiner", value=tamplate_exam_data["professor"])
                st.markdown("\n")
                st.subheader("Task Specification", divider="gray")
                exam_focus = st.text_area(label="Exam Focus", value=tamplate_exam_data["exam_focus"], height=100)
                irr_topics = st.text_area(label="Irrelevant Topics", value=tamplate_exam_data["irr_topics"], height=100)
                c1, c2, c3 = st.columns(3)
                with c1:
                    num_tasks = st.number_input(label="Number of Questions", min_value=1, max_value=40, value=tamplate_exam_data["num_tasks"])
                with c2:
                    num_points = st.number_input(label="Points per Questions", min_value=1, max_value=100, value=tamplate_exam_data["num_points"])
                with c3:
                    st.markdown("")
                    st.markdown("")
                    multi_select = st.toggle("Multi Select", value=tamplate_exam_data["multi_select"])

                template_exam_submit_button = st.form_submit_button(
                    "Create new Exam", 
                    help="Create a new Exam with the same values as this one",
                    use_container_width=True,
                    type="primary"
                )

                if template_exam_submit_button:
                    with st.spinner(f"Generating new Exam from template {exam} ..."):
                        exam_data = {
                            "exam_topic": exam_topic,
                            "university": university,
                            "date": date.strftime("%d.%m.%Y"),
                            "module": class_name,
                            "prof_title": prof_title,
                            "semester": semester,
                            "professor": professor,
                            "exam_focus": exam_focus,
                            "irr_topics": irr_topics,
                            "num_tasks": num_tasks,
                            "num_points": num_points,
                            "multi_select": multi_select
                        }

                        create_new_exam_from_template(new_exam_input, exam_data, current_Exam_DIR)
                        if create_new_exam_from_template:
                            reload_exams(class_name)
                            st.rerun()
                    st.success("Status: Exam successfully created!")

# Add new class
def create_new_page(page_name):
    """Creates a new class and adds it to the list."""
    reload_pages()
    if len(st.session_state.all_pages) < MAX_PAGES:
        class_path = os.path.join(CLASSES_DIR, page_name)
        if os.path.exists(class_path):
            st.warning(f"Class {page_name} already exists!")
        else:
            os.mkdir(class_path)
            st.session_state.all_pages.append(page_name)
            st.success(f"Class {page_name} created successfully!")
            st.session_state.current_page = page_name
            st.rerun()
    else:
        st.error(f"Maximum number of classes reached ({MAX_PAGES})!")

# Form for new page
@st.dialog("Create a new Class", width="small")
def newClassForm():
    with st.form(key="new_class_form", clear_on_submit=True):
        new_page_name = st.text_input("Name of new Class")
        submit = st.form_submit_button("Add Class")
        if submit and new_page_name:
            create_new_page(new_page_name)
    

# Sidebar
with st.sidebar:
    if st.button("Home", icon="🏠", type="primary", use_container_width=True):
        st.session_state.current_page = "Home"
    st.title("📚 Class Manager")
    st.write("Manage your classes.")

    if st.button("Create new Class", icon="➕"):
        newClassForm()

    # List of classes
    st.write("### Classes:")
    for page in st.session_state.all_pages:
        if page == ".DS_Store":
            continue
        if st.button(page, key=f"{page}_button", type="primary", use_container_width=True):
            st.session_state.current_page = page

# Main content
if st.session_state.current_page == "Home":
    reload_pages()
    home_page()
else:
    reload_pages()
    class_page(st.session_state.current_page)
