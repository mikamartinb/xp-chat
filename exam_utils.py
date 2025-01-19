import io
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Inches
from model_utils import rag_generate_exam
import os
import json

def create_exam_document(JSON_DIR, vectorstore, page_name):
    # Pfad zum Logo direkt in der Methode definieren
    logo_path = "leuphana_logo.png"  # Ersetze dies durch den tatsächlichen Pfad

    with open(JSON_DIR) as json_file:
        form = json.load(json_file)
        
    exam_string = rag_generate_exam(form, vectorstore)
    
    # Neues Dokument erstellen
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
    # Leere Absätze hinzufügen, um Platz zu schaffen
    for _ in range(5):  # Je nach Bedarf anpassen, hier 15 Absätze für Platz
        doc.add_paragraph()

    # Titel in der Mitte der Seite
    middle_paragraph = doc.add_paragraph()
    middle_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER  # Zentriert
    
    middle_run = middle_paragraph.add_run(f"{form['module']}")  # Titel (page_name)
    middle_run.bold = True
    middle_run.font.size = Pt(24)  # Titel-Schriftgröße 32
    
    for _ in range(7):  # Je nach Bedarf anpassen, hier 15 Absätze für Platz
        doc.add_paragraph()

    # Untertitel (University, Date, Module, Professor, Semester)
    subtitle_paragraph = doc.add_paragraph()
    subtitle_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    subtitle_text = (
        f"{form['university']}\n"
        f"{form['date']}\n"
        f"{form['module']}\n"
        f"{form['professor']}\n"
        f"{form['semester']}"
    )
    subtitle_run = subtitle_paragraph.add_run(subtitle_text)
    subtitle_run.font.size = Pt(12)  # Schriftgröße für den Untertitel

    # Seitenumbruch, um die Fragen auf der nächsten Seite beginnen zu lassen
    doc.add_page_break()

    # Schriftart auf Times New Roman und Schriftgröße 12 einstellen
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)

    # Leere Absätze zu Beginn jeder Frage-Seite einfügen (anpassbar)
    empty_paragraphs_before_questions = 1  # Die Anzahl der leeren Absätze vor den Fragen
    for _ in range(empty_paragraphs_before_questions):
        doc.add_paragraph()  # Leerer Absatz für Platz am Anfang der Seite

    # Ab der zweiten Seite: Fragen einfügen
    lines = exam_string.split("\n")
    block = []  # Zwischenspeicher für einen Block
    question_count = 0  # Zähler für Fragen auf der Seite

    for line in lines:
        line = line.strip()  # Entfernt unnötige Leerzeichen

        if line.startswith("**") and line.endswith("**"):  # Überschrift (z.B. "Question 1")
            if block:  # Vorherigen Block ins Dokument schreiben
                paragraph = doc.add_paragraph()
                for b_line in block:
                    run = paragraph.add_run(b_line)
                    if b_line.endswith("?"):  # Fragen kursiv
                        run.italic = True
                    run.add_break()  # Zeilenumbruch für nächste Zeile
                paragraph.paragraph_format.keep_together = True
                block = []
                question_count += 1

                # Seitenumbruch nach vier Fragen
                if question_count == 4:
                    doc.add_page_break()
                    question_count = 0

                # Leere Absätze zu Beginn jeder neuen Frage-Seite einfügen (anpassbar)
                for _ in range(empty_paragraphs_before_questions):
                    doc.add_paragraph()  # Leerer Absatz für Platz am Anfang der Seite

            # Neue Überschrift (Fragenbezeichner) hinzufügen
            paragraph = doc.add_paragraph()
            question_text = line.strip("**")
            run = paragraph.add_run(f"{question_text} ({form['num_points']} Pt.)")
            run.bold = True  # Fragenbezeichner fett
            paragraph.paragraph_format.keep_with_next = True

        elif line.endswith("?"):  # Kursiv für Fragen
            block.append(line)

        elif line.startswith("Correct Answers:"):  # Richtige Antworten
            block.append(line)

        elif line:  # Normaler Text (Antworten) nur hinzufügen, wenn die Zeile nicht leer ist
            block.append(line)

    # Letzten Block ins Dokument einfügen (falls vorhanden)
    if block:
        paragraph = doc.add_paragraph()
        for b_line in block:
            run = paragraph.add_run(b_line)
            if b_line.endswith("?"):  # Fragen kursiv
                run.italic = True
            run.add_break()  # Zeilenumbruch für nächste Zeile
        paragraph.paragraph_format.keep_together = True

    # Dokument speichern
    
    #TODO: Hier noch anpassen
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()
