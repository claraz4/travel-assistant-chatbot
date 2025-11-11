import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def get_llm(model_name="gemini-2.5-flash", temperature=0.0):
    return ChatGoogleGenerativeAI(
        model=model_name,
        api_key=api_key,
        temperature=temperature
    )
