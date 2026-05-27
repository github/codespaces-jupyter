import os
import json
import requests
from typing import TypedDict, Annotated, List, Union, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_URL = os.getenv("ENGINE_API_URL", "http://localhost:8080/simulate")

# Initialize LLM & Embeddings (Using Gemini 3 since we are in 2026)
llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# Setup Vector Store (ChromaDB)
vector_store = Chroma(
    collection_name="topological_states",
    embedding_function=embeddings
)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The messages"]

@tool
def simulate_market(beta: float = 0.01, kappa: float = 0.1, lambda_cosmo: float = 0.1):
    """
    Simulates BTC-USD market using Quantum-Relativistic dynamics. 
    Use this when the user asks for a simulation or current market status.
    """
    payload = {
        "beta": beta,
        "kappa": kappa,
        "lambda_cosmo": lambda_cosmo,
        "num_states": 4,
        "lyapunov_threshold": 4.20,
        "lambda_meta": 0.05
    }
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            return response.json()
        return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
