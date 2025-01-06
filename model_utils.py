import os
import configparser
import warnings
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
import streamlit as st

warnings.filterwarnings("ignore", category=FutureWarning)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Funktion zur Initialisierung des Modells
def initialize_model(selected_model="meta-llama-3.1-70b-instruct"):
    # API Schlüssel laden
    config = configparser.ConfigParser()
    config_file_path = 'key.secret'
    config.read(config_file_path)
    api_key = config['GWDG']['API_KEY']

    # Base URL für die API
    base_url = "https://chat-ai.academiccloud.de/v1"

    # Modell initialisieren
    return ChatOpenAI(model_name=selected_model, openai_api_key=api_key, openai_api_base=base_url, temperature=0.0)

def create_vector_store(file_paths, model_name="all-MiniLM-L6-v2", save_path="vector_store"):
    """
    Diese Methode lädt mehrere PDFs von den angegebenen Pfaden, erstellt Dokumente mit Metadaten
    und speichert den Vektorspeicher im Arbeitsspeicher.

    Args:
        file_paths (list of str): Liste der Dateipfade zu den PDFs.
        model_name (str): Der Name des verwendeten Embedding-Modells.
        save_path (str): Der Pfad, an dem der Vektorspeicher gespeichert werden soll (nicht genutzt, da Vectorstore im Arbeitsspeicher gehalten wird).

    Returns:
        FAISS: Der erstellte Vektorspeicher.
    """
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    all_documents = []

    for file_path in file_paths:
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()

        for i, page in enumerate(pages):
            document = Document(
                page_content=page.page_content,
                metadata={'source': file_path, 'page': i}
            )
            all_documents.append(document)

    # Erstelle den Vektorspeicher im Arbeitsspeicher
    vector_store = FAISS.from_documents(all_documents, embedding=embeddings)

    return vector_store

def load_or_create_vector_store(file_paths, model_name="all-MiniLM-L6-v2", save_path="vector_store"):
    """
    Diese Methode prüft, ob ein Vektorspeicher existiert. Falls ja, wird er geladen,
    andernfalls wird ein neuer Vektorspeicher erstellt und gespeichert.

    Args:
        file_paths (list of str): Liste der Dateipfade zu den PDFs.
        model_name (str): Der Name des verwendeten Embedding-Modells.
        save_path (str): Der Pfad, an dem der Vektorspeicher gespeichert werden soll.

    Returns:
        FAISS: Der geladene oder neu erstellte Vektorspeicher.
    """
    # In dieser Version speichern wir den Vektorspeicher nur im Arbeitsspeicher
    vector_store = create_vector_store(file_paths, model_name=model_name, save_path=save_path)
    return vector_store

def clear_temp_files():
    """Löscht alle Dateien im temp_files Ordner"""
    temp_dir = "./temp_files"
    if os.path.exists(temp_dir):
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("Temp-Dateien wurden gelöscht.")

def clear_vector_store(page_name):
    """Löscht den Vectorstore aus dem Session-State"""
    if f'vector_store_{page_name}' in st.session_state:
        del st.session_state[f'vector_store_{page_name}']
        print("Vectorstore wurde gelöscht.")
        
def process_string(input_string):
    # Findet die Position des ersten '**'
    start = input_string.find("**")
    if start == -1:
        return "Kein '**' gefunden."

    # Findet die Position der letzten ')'
    end = input_string.rfind(")")
    if end == -1:
        return "Keine schließende Klammer ')' gefunden."

    # Schneidet den String entsprechend zu und behält '**' und ')' bei
    result = input_string[start:end + 1]
    return result



        
def generate_exam(form):
    
    prompt_template = """
    
    ***INSTRUCTIONS***
    You are a Multiple Choice Exam Generator!
    Create a multiple choice exam text with the following instructions: \n
    
    Content focus of the exam: {exam_focus} \n
    
    These are irrelevant topic, which should not me covered by the exam: {irr_topics} \n
    
    This is the number of Question you should create: {num_tasks} \n
    
    If multi_select == 1, multiple answers can be an answer of one question. Half of the questions must have more than one correct answer if multi_select == 1. If multi_select == 0, only one answer can be the answer of one question: multi_select: {multi_select}\n
    
    ***EXAM STRUCTURE***
    Structur the generated text as follows. This must be the Output-Structur
    
    **Question 1**
    Is this a sample question? \n\n
    
    **Answers** \n
    A) \n
    B) \n   
    C) \n
    D) \n
    
    Correct Answers: A) \n
    
    ...
    
    **Question {num_tasks}**
    Is this a sample question? \n\n
    
    **Answers** \n
    A) \n
    B) \n   
    C) \n
    D) \n
    
    Correct Answers: A) & C) \n
    

    Write a quiz text in with this exam structure. You dont need a specific tool. \n
    
    If two Answers are correct use this format: Correct Answers: A) and B) \n
    
    If more than two Answers are correct separate them by comma and use this format: Correct Answers: A), B) and C)
    """
    prompt = PromptTemplate(
        input_variables=["exam_focus", "irr_topics", "num_tasks", "multi_select"], template=prompt_template
    )
    
    llm = initialize_model()
    chain = prompt | llm

    answer = chain.invoke({"exam_focus": form["exam_focus"], "irr_topics": form["irr_topics"], "num_tasks": form["num_tasks"], "multi_select": form["multi_select"]})
    return process_string(answer.content)

def rag_generate_exam(form, vectorstore):
    # Define the prompt template with the 'context' variable for retrieved documents
    
    
    prompt = f"""
    ***INSTRUCTIONS***
    You are a Multiple Choice Exam Generator!
    Create a multiple choice exam text with the following instructions: \n
    
    Content focus of the exam: {form["exam_focus"]} \n
    
    These are irrelevant topics, which should not be covered by the exam: {form["irr_topics"]} \n
    
    This is the number of Questions you should create: {form["num_tasks"]} \n
    
    If multi_select == 1, multiple answers can be an answer of one question. Half of the questions must have more than one correct answer if multi_select == 1. If multi_select == 0, only one answer can be the answer of one question: multi_select: {form["multi_select"]}. However, 50% of all questions must be answered by ONLY one option\n
    
    ***EXAM STRUCTURE***
    Structure the generated text as follows. This must be the Output-Structure:
    
    **Question 1**
    Is this a sample question? \n\n
    
    **Answers** \n
    A) \n
    B) \n   
    C) \n
    D) \n\n
    
    Correct Answers: A) \n
    
    ...
    
    **Question {form["num_tasks"]}**
    Is this a sample question? \n\n
    
    **Answers** \n
    A) \n
    B) \n   
    C) \n
    D) \n\n
    
    Correct Answers: A) & C) \n
    
    If two Answers are correct, use this format: Correct Answers: A) and B) \n
    
    If more than two Answers are correct, separate them by commas and use this format: Correct Answers: A), B) and C). IM
    """


    llm = initialize_model()
    retriever = vectorstore.as_retriever()

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False,
    )

    # Get the answer from the chain
    answer = chain.invoke(prompt)

    # Print the output
    return process_string(answer["result"])
