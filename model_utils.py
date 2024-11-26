import os
import configparser
import warnings
from langchain_openai import ChatOpenAI

warnings.filterwarnings("ignore", category=FutureWarning)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

###LLMs:    "meta-llama-3.1-8b-instruct"       "mistral-large-instruct"     "meta-llama-3.1-70b-instruct"   "qwen2.5-72b-instruct"

# Funktion zur Initialisierung des Modells
def initialize_model(selected_model="mistral-large-instruct"):

    # API Schlüssel laden
    config = configparser.ConfigParser()
    config_file_path = 'key.secret'  # Pfad zur key.secret Datei
    config.read(config_file_path)
    api_key = config['GWDG']['API_KEY']

    # Base URL für die API
    base_url = "https://chat-ai.academiccloud.de/v1"

    # Modell initialisieren
    return ChatOpenAI(model_name=selected_model, openai_api_key=api_key, openai_api_base=base_url, temperature=0.7)
