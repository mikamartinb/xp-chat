import streamlit as st
import os
import io
from docx import Document
from model_utils import create_vector_store, clear_temp_files, clear_vector_store, generate_exam, rag_generate_exam

class PageRenderer:

    def render(self, page_name):
        
        def get_docx(text):
            document = Document()
            document.add_paragraph(text)
            bio = io.BytesIO()
            document.save(bio)
            return bio.getvalue()

        st.write(f"# {page_name}")

        # Zustandsverwaltung für Formularwechsel (nur auf Unterseiten)
        if page_name != "Home":
            if f'form_submitted_{page_name}' not in st.session_state:
                st.session_state[f'form_submitted_{page_name}'] = False
            if f'form_data_{page_name}' not in st.session_state:
                st.session_state[f'form_data_{page_name}'] = {}

            # Logik für PDF-Upload nur auf Unterseiten
            if not st.session_state[f'form_submitted_{page_name}']:
                uploaded_files = st.file_uploader(
                    "Ziehe eine PDF-Datei hierher oder wähle sie aus", 
                    type="pdf", 
                    key=f"uploader_{page_name}",
                    accept_multiple_files=True
                )

            # Formular nur anzeigen, wenn es nicht die Home-Seite ist und nicht bereits abgeschickt wurde
            if not st.session_state[f'form_submitted_{page_name}']:
                with st.form(f"Form_{page_name}", clear_on_submit=True):
                    exam_topic = st.text_input(label="Exam Topic", placeholder="Exam Topic")
                    exam_focus = st.text_area(label="Exam Focus", placeholder="Exam Focus", height=100)
                    irr_topics = st.text_area(label="Irrelevant Topics", placeholder="Irrelevant Topics", height=100)
                    num_tasks = st.number_input(label="Number of Tasks", min_value=1, max_value=40, placeholder="Number of Tasks")
                    max_points = st.number_input(label="Max Points per Tasks", min_value=1, max_value=100, placeholder="Max Points per Task")
                    multi_select = st.toggle("Multi Select")
                    processing_time = st.number_input(label="Processing Time in Minutes", min_value=10, max_value=180, placeholder="Processing Time in Minutes")

                    submit_form = st.form_submit_button("Submit", use_container_width=True, disabled=not uploaded_files)

                    if submit_form:

                        st.session_state[f'form_data_{page_name}'].update({
                            'exam_topic': exam_topic,
                            'exam_focus': exam_focus,
                            'irr_topics': irr_topics,
                            'num_tasks': num_tasks,
                            'max_points': max_points,
                            'multi_select': multi_select,
                            'processing_time': processing_time,
                            'uploaded_files': uploaded_files
                        })
                        st.session_state[f'form_submitted_{page_name}'] = True

                        st.rerun()
            else:
                
                vector_store = None
                if st.button("Generate Exam"):

                    # Temporäre Dateien speichern
                    temp_files = []
                    uploaded_files = st.session_state[f'form_data_{page_name}']["uploaded_files"]
                    for uploaded_file in uploaded_files:
                        temp_file_path = f"./temp_files/{uploaded_file.name}"
                        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
                        with open(temp_file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        temp_files.append(temp_file_path)

                    vector_store = create_vector_store(temp_files)

                    #st.session_state[f'vector_store_{page_name}'] = vector_store

                    st.success("Successfully created Vector Store")
                    
                    # RAG Generated Exam
                    exam_string = rag_generate_exam(vectorstore=vector_store, form=st.session_state[f'form_data_{page_name}'])
                    
                    # Non-RAG Generated Exam
                    #exam_string = generate_exam(form=st.session_state[f'form_data_{page_name}'])
                    
                    st.download_button("Download Exam", data=get_docx(exam_string), file_name=f"Exam_{page_name}.docx", mime="docx")



                    # Nach dem Erstellen den temp_files-Ordner leeren
                    clear_temp_files()

                # Back to Form-Button logik
                if st.button("Back to Form"):
                    # Vor dem Zurückkehren den Vectorstore und die temp_files löschen
                    clear_temp_files()
                    clear_vector_store(page_name)

                    st.session_state[f'form_submitted_{page_name}'] = False
                    st.rerun()
