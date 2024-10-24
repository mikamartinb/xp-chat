import PyPDF2
from model_utils import initialize_model
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA


def generate_questions(pdf_path, llm):
    pdf_name = pdf_path.split("/")[-1]
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
            
    chunk_size = 1000
    chunk_overlap = chunk_size // 10

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    
    chunks = text_splitter.split_text(text=text)
    
    embeddings_model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
    
    prompt = PromptTemplate(
        input_variables=["text"],
        template="""
        Erstelle aus dem folgenden Text Klausurfragen im Format einer Liste von Dictionaries:
        [{
            "question": "Frage?",
            "information": "HIER NICHTS GENERIEREN",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "answer": "Richtige Antwort"
        }]
        Text: {text}
        """
    )
    
    qa_chain = prompt | llm
    return qa_chain.invoke(text)
    

    

# Hauptfunktion
def main():
    pdf_path = "/Users/mika/Desktop/Mika/Studium/7.Semester/AI Project/xp-chat/slides/01_Informationssysteme.pdf"  # Pfad zur PDF-Datei
    llm = initialize_model()
    questions = generate_questions(pdf_path, llm)

    print(questions)

if __name__ == "__main__":
    main()
