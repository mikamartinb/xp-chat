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

# Suppress future warnings from dependencies
warnings.filterwarnings("ignore", category=FutureWarning)
# Disable parallelism for tokenizers to avoid unnecessary warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def initialize_model(selected_model="meta-llama-3.1-70b-instruct"):
    """
    Initialize and return a ChatOpenAI model using the provided configuration.

    This function reads the API key from a configuration file (key.secret)
    and initializes the ChatOpenAI model with the specified parameters.

    Args:
        selected_model (str): The name of the model to use. Defaults to "meta-llama-3.1-70b-instruct".

    Returns:
        ChatOpenAI: An instance of the ChatOpenAI model configured with the API key and base URL.
    """
    # Load API key from config file
    config = configparser.ConfigParser()
    config_file_path = 'key.secret'
    config.read(config_file_path)
    api_key = config['GWDG']['API_KEY']

    # Define the base URL for the API
    base_url = "https://chat-ai.academiccloud.de/v1"

    # Return the initialized model instance
    return ChatOpenAI(model_name=selected_model, openai_api_key=api_key, openai_api_base=base_url, temperature=0.0)


def create_vector_store(file_paths, save_path, model_name="all-MiniLM-L6-v2"):
    """
    Create and return a vector store from a list of PDF file paths.

    The function loads each PDF, splits it into pages, creates Document objects
    with associated metadata, and builds a vector store using HuggingFaceEmbeddings.
    The vector store is saved locally at the specified path.

    Args:
        file_paths (list of str): List of file paths to PDF documents.
        save_path (str): The local path where the vector store should be saved.
                         (Note: Although the vector store is built in memory,
                         it is also saved locally.)
        model_name (str): The name of the embedding model to use. Defaults to "all-MiniLM-L6-v2".

    Returns:
        FAISS: The created vector store.
    """
    # Initialize embeddings model
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    all_documents = []

    # Process each PDF file
    for file_path in file_paths:
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()

        # Create Document objects for each page with metadata
        for i, page in enumerate(pages):
            document = Document(
                page_content=page.page_content,
                metadata={'source': file_path, 'page': i}
            )
            all_documents.append(document)

    # Build the vector store from the documents and save it locally
    vector_store = FAISS.from_documents(all_documents, embedding=embeddings)
    vector_store.save_local(save_path)
    return vector_store


def load_or_create_vector_store(file_paths, model_name="all-MiniLM-L6-v2", save_path="vector_store"):
    """
    Load an existing vector store or create a new one from the given PDF file paths.

    In this implementation, the vector store is always created and stored locally,
    regardless of whether one already exists.

    Args:
        file_paths (list of str): List of file paths to PDF documents.
        model_name (str): The name of the embedding model to use. Defaults to "all-MiniLM-L6-v2".
        save_path (str): The path where the vector store will be saved. Defaults to "vector_store".

    Returns:
        FAISS: The loaded or newly created vector store.
    """
    # In this version, the vector store is always created fresh
    vector_store = create_vector_store(file_paths, save_path=save_path, model_name=model_name)
    return vector_store


def process_string(input_string):
    """
    Process the input string by extracting a substring starting at the first '**'
    and ending at the last closing parenthesis ')'.

    Args:
        input_string (str): The string to process.

    Returns:
        str: The extracted substring if both delimiters are found,
             otherwise an error message indicating the missing delimiter.
    """
    # Find the position of the first '**'
    start = input_string.find("**")
    if start == -1:
        return "No '**' found."

    # Find the position of the last ')'
    end = input_string.rfind(")")
    if end == -1:
        return "No closing bracket ')' found."

    # Return the substring including the '**' and the closing ')'
    result = input_string[start:end + 1]
    return result


def generate_exam(form):
    """
    Generate a multiple choice exam text based on the provided form data.

    The function uses a prompt template to instruct the language model to create
    an exam. The generated output is then processed to extract the relevant section.

    Args:
        form (dict): A dictionary containing the following keys:
            - "exam_focus": The focus content of the exam.
            - "irr_topics": Topics that should be excluded.
            - "num_tasks": The number of questions to generate.
            - "multi_select": Flag indicating if multiple answers per question are allowed.

    Returns:
        str: The processed exam text.
    """
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
    # Initialize the prompt template with expected variables
    prompt = PromptTemplate(
        input_variables=["exam_focus", "irr_topics", "num_tasks", "multi_select"],
        template=prompt_template
    )
    
    # Initialize the language model
    llm = initialize_model()
    # Chain the prompt and the model (using the overloaded operator for chaining)
    chain = prompt | llm

    # Invoke the chain with form values and process the output
    answer = chain.invoke({
        "exam_focus": form["exam_focus"],
        "irr_topics": form["irr_topics"],
        "num_tasks": form["num_tasks"],
        "multi_select": form["multi_select"]
    })
    return process_string(answer.content)


def rag_generate_exam(form, vectorstore):
    """
    Generate a multiple choice exam using a retrieval-augmented generation (RAG) approach.

    This function builds a prompt that includes the exam instructions and then uses a
    retriever from the vector store to provide context to the language model. The output
    is processed to extract the relevant exam text.

    Args:
        form (dict): A dictionary containing exam parameters with the following keys:
            - "exam_focus": Focus content for the exam.
            - "irr_topics": Topics to exclude.
            - "num_tasks": Number of questions to generate.
            - "multi_select": Flag indicating whether multiple answers per question are allowed.
        vectorstore (FAISS): The vector store to be used for retrieving context documents.

    Returns:
        str: The processed exam text.
    """
    # Build the prompt by directly inserting form values
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
    
    ++Answers++ \n
    A) \n
    B) \n   
    C) \n
    D) \n\n
    
    Correct Answers: A) & C) \n
    
    If two Answers are correct, use this format: Correct Answers: A) and B) \n
    
    If more than two Answers are correct, separate them by commas and use this format: Correct Answers: A), B) and C). IM
    
    Do not add ** before or after Correct Answers. 
    """
    # Initialize the language model
    llm = initialize_model()
    # Create a retriever from the vector store
    retriever = vectorstore.as_retriever()

    # Create a RetrievalQA chain using the language model and retriever
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False,
    )

    # Invoke the chain with the prompt and process the result
    answer = chain.invoke(prompt)
    return process_string(answer["result"])
