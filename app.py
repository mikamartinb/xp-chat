import json
from model_utils import create_vector_store
from exam_utils import create_exam_document
import streamlit as st
import os
from datetime import datetime
import io, zipfile
from time import sleep as time

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

# Home page
def home_page():
    st.title("Welcome to the Class Manager!")
    st.write("Select a class in the sidebar or create a new class.")

# New Form Exam Page
def newExam(new_exam_name):
    st.title(f"New Exam: {new_exam_name}")


# Class page
def class_page(class_name):
    CurrentClassDIR = os.path.join(CLASSES_DIR, class_name)

    if "all_exams_in_class" not in st.session_state:
        st.session_state.all_exams_in_class = os.listdir(CurrentClassDIR)

    # Create new exam folder and redirect to Exam Form 
    def create_new_exam(new_exam_name):
        """Creates a new exam in the specified class."""
        new_exam_DIR = os.path.join(CurrentClassDIR, new_exam_name)
        if os.path.exists(new_exam_name):
            st.toast(f"Exam :green[{new_exam_name}] already exists!")
            return False
        else:
            NewExam = newExamName(new_exam_DIR, new_exam_name)
            if NewExam:
                return True
            else:
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
                        return True
                    else:
                        return False
                        print("Error creating Exam")
                else:
                    return False
                    print("Error creating Vector Store")

    # Page Information
    st.title(f"Class: :green[{class_name}]")
    with st.form(key="new_exam_name_form", clear_on_submit=True):
        new_exam_name = st.text_input("Name of new Exam", placeholder="Name of new Exam")
        submit = st.form_submit_button("Create a new Exam")
        if submit and new_exam_name:
            Exam_creation = create_new_exam(new_exam_name)
            reload_exams(class_name)
            if Exam_creation:
                st.toast(f"Exam :green[{new_exam_name}] created successfully!", icon="🎉")
                time(3)
                st.rerun()
            else:
                st.toast(f"Error creating Exam :green[{new_exam_name}] !", icon="🚫")   
    
    #List all Exams in the Class
    st.write("### Exams:")
    for exam in st.session_state.all_exams_in_class:
        with st.expander(exam):
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


            col1, col2 = st.columns(2)
            with col1:
                if st.button("Use as template", key=f"{exam}_templateButton", disabled=True):
                    st.write(f"Creates Template for {exam}")
            with col2:
                if st.download_button(
                label=f"Download {exam}",
                data=download_all_exams(),
                file_name=f"{exam}.zip",
                key=f"{exam}_downloadButton"
                ):
                    st.toast(f"Downloading... :green[{exam}.zip]", icon="📥")

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
