import io
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Inches
from model_utils import rag_generate_exam
#from docx2pdf import convert
#import pypandoc
import os 
import json

def create_exam_document(JSON_DIR, vectorstore, page_name, output_DIR):

    with open(JSON_DIR) as json_file:
        form = json.load(json_file)

    # create folder DOCX and PDF
    if not os.path.exists(os.path.join(output_DIR, "DOCX")):
        os.makedirs(os.path.join(output_DIR, "DOCX"))
    if not os.path.exists(os.path.join(output_DIR, "PDF")):
        os.makedirs(os.path.join(output_DIR, "PDF"))

        
    exam_with_docx = f"{page_name}_exam_with_answers.docx"
    exam_without_docx = f"{page_name}_exam_without_answers.docx"
    
    exam_with_DIR_docx = os.path.join(output_DIR, "DOCX", exam_with_docx)
    exam_without_DIR_docx = os.path.join(output_DIR, "DOCX", exam_without_docx)

    exam_with_pdf = f"{page_name}_exam_with_answers.pdf"
    exam_without_pdf = f"{page_name}_exam_without_answers.pdf"

    exam_with_DIR_pdf = os.path.join(output_DIR, "PDF", exam_with_pdf)
    exam_without_DIR_pdf = os.path.join(output_DIR, "PDF", exam_without_pdf)

    print(f"Der Pfade vom mit output docx: {exam_with_DIR_docx}")
    print(f"Der Pfade vom ohne output docx: {exam_without_DIR_docx}")

    print(f"Der Pfade vom mit output pdf: {exam_with_DIR_pdf}")
    print(f"Der Pfade vom ohne output pdf: {exam_without_DIR_pdf}")

    print(f"Was ist hier im Vector Store?: {vectorstore}")

    print("Form data loaded from JSON:")
    for key, value in form.items():
        print(f"{key}: {value}")
    
    # Pfad zum Logo direkt in der Methode definieren
    logo_path = "public/leuphana_logo.png"  # Ersetze dies durch den tatsächlichen Pfad

    exam_string = rag_generate_exam(form, vectorstore)

    if exam_string:
        print("Exam generated successfully.")
    else:    
        print("Error generating exam with Json Data or vectorstore")
        return False

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
    if doc_with_answers:
        print("Document with answers created successfully.")
    else:
        print("Failed to create document with answers.")
        return False

    doc_without_answers = create_document(filter_correct_answers=True)
    if doc_without_answers:
        print("Document without answers created successfully.")
    else:
        print("Failed to create document without answers.")
        return False

    try:
        doc_with_answers.save(exam_with_DIR_docx)
        print(f"Document with answers saved successfully at {exam_with_DIR_docx}.")
    except Exception as e:
        print(f"Failed to save document with answers: {e}")
        return False

    try:
        doc_without_answers.save(exam_without_DIR_docx)
        print(f"Document without answers saved successfully at {exam_without_DIR_docx}.")
    except Exception as e:
        print(f"Failed to save document without answers: {e}")
        return False

    # PDF-Konvertierung wurde vor erst einmal auskommentiert
    #try:
    #    #convert(exam_with_DIR_docx, exam_with_DIR_pdf)
    #    pypandoc.convert_file(exam_with_DIR_docx, 'pdf', outputfile=exam_without_DIR_pdf, extra_args=['--pdf-engine=xelatex'])
    #    print(f"PDF conversion for document with answers successful at {exam_with_DIR_pdf}")
    #except Exception as e:
    #    print(f"Failed to convert document with answers to PDF: {e}")
    #    return False

    #try:
    #    #convert(exam_without_DIR_docx, exam_without_DIR_pdf)
    #    pypandoc.convert_file(exam_without_DIR_docx, 'pdf', outputfile=exam_without_DIR_pdf, extra_args=['--pdf-engine=xelatex'])
    #    print(f"PDF conversion for document without answers successful at {exam_without_DIR_pdf}")
    #except Exception as e:
    #    print(f"Failed to convert document without answers to PDF: {e}")
    #    return False

    return True