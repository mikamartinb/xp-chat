import json
import os
import io
import zipfile
import shutil
from datetime import datetime

import streamlit as st
from model_utils import create_vector_store
from exam_utils import create_exam_document

# Constants
MAX_PAGES = 6  # Maximum number of classes allowed
CLASSES_DIR = "Classes"

# Ensure the "Classes" folder exists
if not os.path.exists(CLASSES_DIR):
    os.mkdir(CLASSES_DIR)

# Initialize global session state variables
if "all_pages" not in st.session_state:
    st.session_state.all_pages = os.listdir(CLASSES_DIR)

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

if "privacy_accepted" not in st.session_state:
    st.session_state.privacy_accepted = False


def reload_pages():
    """
    Reload the list of class pages by reading the directory.

    This function updates the session state's "all_pages" variable.

    Returns:
        None
    """
    st.session_state.all_pages = os.listdir(CLASSES_DIR)


def reload_exams(class_name):
    """
    Reload the list of exams for a given class.

    Args:
        class_name (str): The name of the class.

    Returns:
        None
    """
    current_class_dir = os.path.join(CLASSES_DIR, class_name)
    st.session_state.all_exams_in_class = os.listdir(current_class_dir)


# Privacy Dialog (displayed if privacy not yet accepted)
if not st.session_state.privacy_accepted:
    @st.dialog("Datenschutzhinweise", width="medium")
    def privacy_dialog():
        """
        Display the privacy policy dialog and handle acceptance or decline.

        Returns:
            None
        """
        st.write("Bitte lese die Datenschutzhinweise und bestätige diese um diese App zu nutzen :)")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Ablehnen", key="privacy_decline"):
                st.error("Sie müssen den Datenschutzhinweisen zustimmen, um die App nutzen zu können.")
        with col3:
            if st.button("Annehmen", key="privacy_accept"):
                st.session_state.privacy_accepted = True
                st.toast("Danke, dass Sie den Datenschutzhinweisen zugestimmt haben.")
                st.rerun()
        with col2:
            # Allow the user to download the privacy policy document
            if st.download_button(
                "Download Datenschutzhinweise",
                data=open("public/Datenschutz/Datenschutz_Hinweise_oeffentliche_Aufgabe_7.03.docx", "rb").read(),
                file_name="Datenschutz_Hinweise_oeffentliche_Aufgabe_7.03.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ):
                st.toast("Datenschutzhinweise heruntergeladen.")

    privacy_dialog()


@st.dialog("Delete Class", width="small")
def delete_page(page_name):
    """
    Delete a class directory and remove it from the session state's list.

    Args:
        page_name (str): The name of the class to be deleted.

    Returns:
        None
    """
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


def home_page():
    """
    Render the home page with a list of classes and options to create a new class.

    Returns:
        None
    """
    c1, c2, c3 = st.columns(3)
    with c2:
        st.image("public/XP-CHAT.png", use_column_width=True)
    st.title("Welcome to the Class Manager!")
    if st.button("Create new Class", icon="➕", key="new_class_button", use_container_width=True, type="primary"):
        newClassForm()
    st.write("### Classes:")
    with st.container():
        for page in st.session_state.all_pages:
            # Skip hidden/system files
            if page == ".DS_Store":
                continue
            with st.container():
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.subheader(f":green[{page}]")
                with col2:
                    # Open the selected class page
                    if st.button(f"Open **{page}** ➡️", key=f"Home_{page}_button", type="primary", use_container_width=True):
                        st.session_state.current_page = page
                with col3:
                    if st.button("Delete", key=f"delete_{page}"):
                        delete_page(page)


def class_page(class_name):
    """
    Render the class page where exams are managed, created, or deleted.

    Args:
        class_name (str): The name of the class.

    Returns:
        None
    """
    reload_exams(class_name)
    current_class_dir = os.path.join(CLASSES_DIR, class_name)

    if "all_exams_in_class" not in st.session_state:
        st.session_state.all_exams_in_class = os.listdir(current_class_dir)

    @st.fragment()
    def create_new_exam(new_exam_name):
        """
        Create a new exam folder within the class and open the exam form dialog.

        Args:
            new_exam_name (str): The name of the new exam.

        Returns:
            bool: Always returns False to avoid further processing in the fragment.
        """
        new_exam_DIR = os.path.join(current_class_dir, new_exam_name)
        if os.path.exists(new_exam_DIR):
            st.toast(f"Exam :green[{new_exam_name}] already exists!")
            return False
        else:
            # Call the dialog to create a new exam with detailed information.
            NewExam = newExamName(new_exam_DIR, new_exam_name)
            if NewExam:
                st.rerun()  # Refresh to update the exam list
            return False

    @st.dialog("Create a new Exam", width="large")
    def newExamName(new_exam_DIR, new_exam_name):
        """
        Display a form to create a new exam and process the provided inputs.

        Args:
            new_exam_DIR (str): Directory path where the exam will be created.
            new_exam_name (str): The name of the new exam.

        Returns:
            bool: True if exam creation was successful; otherwise, False.
        """
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
                semester = st.selectbox(
                    label="Semester",
                    options=["Wintersemester 2024/2025", "Sommersemester 2025", "Wintersemester 2025/2026", "Sommersemester 2026"],
                    placeholder="Choose a Semester"
                )
            with c2:
                prof_title = st.selectbox(
                    label="Title",
                    options=["B. A.", "B. Sc.", "M. A.", "M. Sc.", "Dr.", "Prof.", "Prof. Dr.", "Prof. Dr. Dr."],
                    placeholder="Choose Title",
                    index=0
                )
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

                    # Save uploaded PDFs to input directory and store their paths
                    pdf_input_DIR = os.path.join(new_exam_DIR, "pdf_input")
                    os.mkdir(pdf_input_DIR)
                    for uploaded_file in uploaded_files:
                        current_uploaded_pdf = os.path.join(pdf_input_DIR, uploaded_file.name)
                        with open(current_uploaded_pdf, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        all_input_pdf_files.append(current_uploaded_pdf)

                    # Build vector store from uploaded PDFs
                    vector_store_DIR = os.path.join(new_exam_DIR, "vector_store")
                    vector_store = create_vector_store(all_input_pdf_files, vector_store_DIR)

                    # Create output directory
                    output_DIR = os.path.join(new_exam_DIR, "output")
                    os.mkdir(output_DIR)

                    # Create exam documents using the vector store
                    if vector_store:
                        createExam = create_exam_document(exam_json_file_DIR, vector_store, class_name, output_DIR)
                        if createExam:
                            reload_exams(class_name)
                            st.rerun()
        return True  # If the form completes successfully

    @st.dialog("Delete Exam", width="small")
    def delete_exam(exam_name):
        """
        Delete an exam folder from the class and update the exam list.

        Args:
            exam_name (str): The name of the exam to be deleted.

        Returns:
            None
        """
        exam_path = os.path.join(current_class_dir, exam_name)
        st.write(f"Are you sure you want to delete the Exam {exam_name}...")
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

    @st.fragment()
    def create_new_exam_from_template(new_exam_input, exam_data, old_exam_DIR):
        """
        Create a new exam based on an existing exam template.

        Args:
            new_exam_input (str): The name for the new exam.
            exam_data (dict): The exam configuration data.
            old_exam_DIR (str): The directory of the exam to use as a template.

        Returns:
            bool: True if the new exam was created successfully, False otherwise.
        """
        new_exam_DIR = os.path.join(current_class_dir, new_exam_input)
        # Check if the exam folder already exists using the proper directory path
        if os.path.exists(new_exam_DIR):
            st.toast(f"Exam :green[{new_exam_input}] already exists!")
            return False
        else:
            # Create exam folder and save exam data to a JSON file
            os.mkdir(new_exam_DIR)
            exam_json_file_DIR = os.path.join(new_exam_DIR, f"{new_exam_input}.json")
            with open(exam_json_file_DIR, "w") as json_file:
                json.dump(exam_data, json_file, indent=4)

            # Copy PDFs from the template exam to the new exam folder
            new_exam_input_PDF_DIR = os.path.join(new_exam_DIR, "pdf_input")
            os.mkdir(new_exam_input_PDF_DIR)
            old_exam_input_PDF_DIR = os.path.join(old_exam_DIR, "pdf_input")
            for file in os.listdir(old_exam_input_PDF_DIR):
                shutil.copy(os.path.join(old_exam_input_PDF_DIR, file), new_exam_input_PDF_DIR)

            # Create output directory for the new exam
            output_DIR = os.path.join(new_exam_DIR, "output")
            os.mkdir(output_DIR)

            # Build vector store from the copied PDFs
            pdf_input_DIR = os.path.join(new_exam_DIR, "pdf_input")
            all_input_pdf_files = [os.path.join(pdf_input_DIR, file) for file in os.listdir(pdf_input_DIR)]
            vector_store_DIR = os.path.join(new_exam_DIR, "vector_store")
            vector_store = create_vector_store(all_input_pdf_files, vector_store_DIR)

            # Generate the exam documents using the vector store
            createExam = create_exam_document(exam_json_file_DIR, vector_store, class_name, output_DIR)
            if createExam:
                return True
            else:
                return False

    @st.fragment()
    def delete_exam_button(exam_name):
        """
        Render a delete button for an exam and call the delete_exam dialog when pressed.

        Args:
            exam_name (str): The name of the exam.

        Returns:
            None
        """
        if st.button("Delete", key=f"delete_{exam_name}", help="Delete this Exam", use_container_width=True):
            delete_exam(exam_name)

    # Page header showing current class
    st.title(f"Class: :green[{class_name}]")
    with st.form(key="new_exam_name_form", clear_on_submit=True):
        new_exam_name = st.text_input("Name of new Exam", placeholder="Name of new Exam")
        submit = st.form_submit_button("Create a new Exam")
        if submit and new_exam_name:
            create_new_exam(new_exam_name)
            reload_exams(class_name)

    # List all exams in the class
    st.write("### Exams:")
    for exam in st.session_state.all_exams_in_class:
        # Inject custom CSS for the expander header
        st.markdown("""
            <style>
                [data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] p {
                    font-size: 25px !important;
                    font-weight: bold !important;
                    border: 2px solid #0FA37F !important;
                    border-radius: 5px !important;
                    color: #F0F0F0 !important;
                    padding-top: 2px !important;
                    padding-bottom: 2px !important;
                    padding-left: 10px !important;
                    padding-right: 10px !important;
                    background-color: #0FA37F !important;
                }
            </style>
            """, unsafe_allow_html=True)
        with st.expander(f"**{exam}**", expanded=False):
            current_exam_DIR = os.path.join(current_class_dir, exam)

            def download_all_exams():
                """
                Package all exam documents (PDF and DOCX) into a zip file for download.

                Returns:
                    bytes: The binary data of the zip file.
                """
                pdf_files_DIR = os.path.join(current_exam_DIR, "output", "PDF")
                docx_files_DIR = os.path.join(current_exam_DIR, "output", "DOCX")
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

            # Form to use an existing exam as a template to create a new exam
            st.subheader("Use as template to create a new Exam: ")
            with st.form(key=f"edit_{exam}_form", clear_on_submit=True):
                new_exam_input = st.text_input("Name of new Exam", key=f"edit_{exam}_input", placeholder="Name of new Exam")
                with open(os.path.join(current_exam_DIR, f"{exam}.json")) as current_json_file:
                    template_exam_data = json.load(current_json_file)
                st.subheader("General Information", divider="gray")
                exam_topic = st.text_input(label="Exam Topic", value=template_exam_data["exam_topic"])
                university = st.text_input(label="University", value=template_exam_data["university"])
                date = st.date_input(label="Date of the exam", value=datetime.strptime(template_exam_data["date"], "%d.%m.%Y"), format="DD.MM.YYYY")
                c1, c2 = st.columns(2)
                with c1:
                    semesters = ["Wintersemester 2024/2025", "Sommersemester 2025", "Wintersemester 2025/2026", "Sommersemester 2026"]
                    try:
                        semester_index = semesters.index(template_exam_data["semester"])
                    except ValueError:
                        semester_index = 0
                    semester = st.selectbox("Semester", semesters, index=semester_index)
                with c2:
                    titles = ["B. A.", "B. Sc.", "M. A.", "M. Sc.", "Dr.", "Prof.", "Prof. Dr.", "Prof. Dr. Dr."]
                    try:
                        title_index = titles.index(template_exam_data["prof_title"])
                    except ValueError:
                        title_index = 0
                    prof_title = st.selectbox("Title", titles, index=title_index)
                professor = st.text_input(label="Examiner", value=template_exam_data["professor"])
                st.markdown("\n")
                st.subheader("Task Specification", divider="gray")
                exam_focus = st.text_area(label="Exam Focus", value=template_exam_data["exam_focus"], height=100)
                irr_topics = st.text_area(label="Irrelevant Topics", value=template_exam_data["irr_topics"], height=100)
                c1, c2, c3 = st.columns(3)
                with c1:
                    num_tasks = st.number_input(label="Number of Questions", min_value=1, max_value=40, value=template_exam_data["num_tasks"])
                with c2:
                    num_points = st.number_input(label="Points per Questions", min_value=1, max_value=100, value=template_exam_data["num_points"])
                with c3:
                    st.markdown("")
                    st.markdown("")
                    multi_select = st.toggle("Multi Select", value=template_exam_data["multi_select"])

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
                        # Capture the result of exam creation from the template
                        result = create_new_exam_from_template(new_exam_input, exam_data, current_exam_DIR)
                        if result:
                            reload_exams(class_name)
                            st.rerun()
                    st.success("Status: Exam successfully created!")


def create_new_page(page_name):
    """
    Create a new class folder and add it to the session state's list if within allowed limits.

    Args:
        page_name (str): The name of the new class.

    Returns:
        None
    """
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


@st.dialog("Create a new Class", width="small")
def newClassForm():
    """
    Display a form to create a new class.

    Returns:
        None
    """
    with st.form(key="new_class_form", clear_on_submit=True):
        new_page_name = st.text_input("Name of new Class")
        submit = st.form_submit_button("Add Class")
        if submit and new_page_name:
            create_new_page(new_page_name)


# Sidebar content for navigation and class creation
with st.sidebar:
    st.image("public/xpchat_logo.png", width=200)

    if st.button("Home", icon="🏠", type="primary", use_container_width=True):
        st.session_state.current_page = "Home"
    st.title("📚 Class Manager")
    st.write("Manage your classes.")

    if st.button("Create new Class", icon="➕"):
        newClassForm()

    st.write("### Classes:")
    for page in st.session_state.all_pages:
        if page == ".DS_Store":
            continue
        if st.button(page, key=f"{page}_button", type="primary", use_container_width=True):
            st.session_state.current_page = page

# Main content: render either the home page or the selected class page
if st.session_state.current_page == "Home":
    reload_pages()
    home_page()
else:
    reload_pages()
    class_page(st.session_state.current_page)
