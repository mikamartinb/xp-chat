import io
import os
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Inches
from model_utils import rag_generate_exam
from docx2pdf import convert
import shutil

def create_exam_document(form, vectorstore, page_name):
    # Ordner und Dateipfad definieren
    output_folder = "generated_exams"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)  # Ordner erstellen, falls er nicht existiert

    filename = f"{page_name}_exam.docx"
    filtered_filename = f"{page_name}_exam_filtered.docx"
    file_path = os.path.join(output_folder, filename)
    filtered_file_path = os.path.join(output_folder, filtered_filename)

    # Pfad zum Logo direkt in der Methode definieren
    logo_path = "leuphana_logo.png"  # Ersetze dies durch den tatsächlichen Pfad

    exam_string = rag_generate_exam(form, vectorstore)

    # Funktion, um ein Dokument zu erstellen
    def create_document(filter_correct_answers=False):
        doc = Document()

        # Logo in den Header hinzufügen
        section = doc.sections[0]
        header = section.header
        header_paragraph = header.paragraphs[0]
        header_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER  # Logo zentrieren
        run = header_paragraph.add_run()
        try:
            run.add_picture(logo_path, width=Inches(2))  # Logo (Breite: 2 Zoll)
        except Exception as e:
            print(f"Error when adding the logo to the header: {e}")

        # Erste Seite: Nur Titel in der Mitte der Seite
        for _ in range(5):
            doc.add_paragraph()

        middle_paragraph = doc.add_paragraph()
        middle_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        middle_run = middle_paragraph.add_run(f"{form['module']}")
        middle_run.bold = True
        middle_run.font.size = Pt(24)

        for _ in range(7):
            doc.add_paragraph()

        subtitle_paragraph = doc.add_paragraph()
        subtitle_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        subtitle_text = (
            f"{form['university']}\n"
            f"{form['date']}\n"
            f"{form['module']}\n"
            f"{form['professor']}\n"
            f"{form['semester']}\n"
            f"Total: {form['num_tasks'] * form['num_points']} Pt."
        )
        subtitle_run = subtitle_paragraph.add_run(subtitle_text)
        subtitle_run.font.size = Pt(12)

        doc.add_page_break()

        style = doc.styles['Normal']
        style.font.name = 'Times New Roman'
        style.font.size = Pt(12)

        empty_paragraphs_before_questions = 1
        for _ in range(empty_paragraphs_before_questions):
            doc.add_paragraph()

        lines = exam_string.split("\n")
        block = []
        question_count = 0

        for line in lines:
            line = line.strip()

            if line.startswith("**") and line.endswith("**"):
                if block:
                    paragraph = doc.add_paragraph()
                    for b_line in block:
                        run = paragraph.add_run(b_line)
                        if b_line.endswith("?"):
                            run.italic = True
                        run.add_break()
                    paragraph.paragraph_format.keep_together = True
                    block = []
                    question_count += 1

                    if question_count == 4:
                        doc.add_page_break()
                        question_count = 0

                    for _ in range(empty_paragraphs_before_questions):
                        doc.add_paragraph()

                paragraph = doc.add_paragraph()
                question_text = line.strip("**")
                run = paragraph.add_run(f"{question_text} ({form['num_points']} Pt.)")
                run.bold = True
                paragraph.paragraph_format.keep_with_next = True

            elif line.startswith("++") and line.endswith("++"):
                if block:
                    paragraph = doc.add_paragraph()
                    for b_line in block:
                        run = paragraph.add_run(b_line)
                        if b_line.endswith("?"):
                            run.italic = True
                        run.add_break()
                    paragraph.paragraph_format.keep_together = True
                    block = []

                paragraph = doc.add_paragraph()
                text = line.strip("++")
                run = paragraph.add_run(text)
                run.bold = True

            elif line.endswith("?"):
                block.append(line)

            elif line.startswith("Correct Answers:"):
                if not filter_correct_answers:
                    block.append(line)

            elif line:
                block.append(line)

        if block:
            paragraph = doc.add_paragraph()
            for b_line in block:
                run = paragraph.add_run(b_line)
                if b_line.endswith("?"):
                    run.italic = True
                run.add_break()
            paragraph.paragraph_format.keep_together = True

        return doc

    # Dokumente erstellen und speichern
    doc_with_answers = create_document()
    doc_without_answers = create_document(filter_correct_answers=True)

    doc_with_answers.save(file_path)
    doc_without_answers.save(filtered_file_path)

    # PDF-Konvertierung
    convert(file_path)
    convert(filtered_file_path)

    # Archiv erstellen
    shutil.make_archive(f"{output_folder}/{page_name}_exam", "zip", output_folder)

    bio = io.BytesIO()
    return bio.getvalue()
