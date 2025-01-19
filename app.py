import json
from model_utils import create_vector_store
import streamlit as st
import os
from datetime import datetime

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
            st.warning(f"Exam '{new_exam_name}' already exists!")
        else:
            os.mkdir(new_exam_DIR)
            st.success(f"Exam '{new_exam_name}' created successfully!")
            newExamName(new_exam_DIR, new_exam_name)


    # Create new exam name
    @st.dialog("Create a new Exam", width="large")
    def newExamName(new_exam_DIR, new_exam_name):
        all_input_pdf_files = []
        with st.form(key="new_exam_form"):
            uploaded_files = st.file_uploader(
                "Upload one or more PDFs before generation", 
                type="pdf", 
                key=f"uploader_{new_exam_name}",
                accept_multiple_files=True
            )
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
                num_tasks = st.number_input(label="Number of Tasks", min_value=1, max_value=40, placeholder="Number of Tasks")
            with c2:
                num_points = st.number_input(label="Points per Tasks", min_value=1, max_value=100, placeholder="Points per Task")
            with c3:
                st.markdown("")
                st.markdown("")
                multi_select = st.toggle("Multi Select")
            

            submit_form = st.form_submit_button("Generate", use_container_width=True)

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
                exam_json_file_DIR = os.path.join(new_exam_DIR, f"{new_exam_name}.json")
                with open(exam_json_file_DIR, "w") as json_file:
                    json.dump(exam_data, json_file, indent=4)
                pdf_input_DIR = os.path.join(new_exam_DIR, "pdf_input")
                os.mkdir(pdf_input_DIR)
                for uploaded_file in uploaded_files:
                    current_uploaded_pdf = os.path.join(pdf_input_DIR, uploaded_file.name)
                    with open(current_uploaded_pdf, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    all_input_pdf_files.append(current_uploaded_pdf)
                vector_store_DIR = os.path.join(new_exam_DIR, "vector_store")
                st.toast(f"Die files paths sind: {all_input_pdf_files}")
                st.toast(f"Der Vektordatenbank speicher path ist: {vector_store_DIR}")

                if create_vector_store(all_input_pdf_files, vector_store_DIR):
                    st.success(f"PDFs for '{new_exam_name}' saved successfully!")
                    # hier muss die Logik die Exams zu erstellen 
                    #if create_exam_from_vector_store(vector_store_DIR, exam_json_file_DIR):
                        #st.success(f"PDFs for '{new_exam_name}' saved successfully!")
                        # st.rerun()
                    #else:
                        #st.error(f"Error creating Exams for '{new_exam_name}'")
                else:
                    st.error(f"Error creating Vector Store and saving PDFs for '{new_exam_name}'")

    # Page Information
    st.title(f"Class: {class_name}")
    st.write(f"This is the page for class **{class_name}**.")
    with st.form(key="new_exam_name_form"):
            new_exam_name = st.text_input("Name of new Exam", placeholder="Name of new Exam")
            submit = st.form_submit_button("Create a new Exam")
            if submit and new_exam_name:
                create_new_exam(new_exam_name)
    
    #List all Exams in the Class
    st.write("### Exams:")
    for exam in st.session_state.all_exams_in_class:
        with st.expander(exam):
            col1, col2 = st.columns(2)
            with col1:
                st.write("Here comes the PDF Viwer")
            with col2:
                st.write("This is an exam.")
                if st.button("Edit"):
                    st.session_state.current_page = exam

# Add new class
def create_new_page(page_name):
    """Creates a new class and adds it to the list."""
    if len(st.session_state.all_pages) < MAX_PAGES:
        class_path = os.path.join(CLASSES_DIR, page_name)
        if os.path.exists(class_path):
            st.warning(f"Class '{page_name}' already exists!")
        else:
            os.mkdir(class_path)
            st.session_state.all_pages.append(page_name)
            st.success(f"Class '{page_name}' created successfully!")
            st.session_state.current_page = page_name
            st.rerun()
    else:
        st.error(f"Maximum number of classes reached ({MAX_PAGES})!")

# Form for new page
@st.dialog("Create a new Class", width="small")
def newClassForm():
    with st.form(key="new_class_form"):
        new_page_name = st.text_input("Name of new Class")
        submit = st.form_submit_button("Add Class")
        if submit and new_page_name:
            create_new_page(new_page_name)
    

# Sidebar
with st.sidebar:
    if st.button("Home"):
        st.session_state.current_page = "Home"
    st.title("📚 Class Manager")
    st.write("Manage your classes.")

    if st.button("Create new Class"):
        newClassForm()

    # List of classes
    st.write("### Classes:")
    for page in st.session_state.all_pages:
        if st.button(page):
            st.session_state.current_page = page

# Main content
if st.session_state.current_page == "Home":
    home_page()
else:
    class_page(st.session_state.current_page)