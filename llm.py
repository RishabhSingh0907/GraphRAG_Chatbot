import streamlit as st
import openai
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_ollama.embeddings import OllamaEmbeddings

# Create the LLM
llm = ChatOpenAI(
    model="openai/gpt-oss-120b",  # Specify the Groq model ID
    api_key=st.secrets["GROQ_API_KEY"],  # Your Groq API key
    base_url="https://api.groq.com/openai/v1",  # Groq's OpenAI-compatible endpoint
)

# Create the Embedding model
embeddings = OllamaEmbeddings(model="mxbai-embed-large")