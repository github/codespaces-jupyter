import os
import json
import requests
from typing import TypedDict, Annotated, List, Union, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_URL = os.getenv("ENGINE_API_URL", "http://localhost:8080/simulate")

# Initialize LLM & Embeddings
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Setup Vector Store (ChromaDB)
vector_store = Chroma(
    collection_name="topological_states",
    embedding_function=embeddings
)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]

@tool
def simulate_market(beta: float = 0.01, kappa: float = 0.1, lambda_cosmo: float = 0.1):
    """
    Triggers the Quantum-Relativistic simulation for BTC-USD. 
    Returns T+1 boundaries, Lyapunov exponent, and Hilbert Norm.
    Call this whenever you need to analyze the current market state.
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
            data = response.json()
            # RAG: Store the state for future retrieval
            if "current_state" in data:
                vector_store.add_texts(
                    texts=[f"State: {json.dumps(data['current_state'])}"],
                    metadatas=[{"type": "simulation_result"}]
                )
            return data
        return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def call_model(state: AgentState):
    # RAG: Retrieve context if user message is analytical
    last_msg = state["messages"][-1].content
    docs = vector_store.similarity_search(last_msg, k=1)
    rag_context = docs[0].page_content if docs else "No relevant historical states found."

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Quantitative Physicist. Analyze the market using topological metrics. "
                   f"Reference Context: {rag_context}\n"
                   "Translate Norm deformations and Chaos limits into strategies. "
                   "Always use the 'simulate_market' tool to get fresh data."),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    chain = prompt | llm.bind_tools([simulate_market])
    response = chain.invoke(state)
    return {"messages": [response]}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode([simulate_market]))

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

app = workflow.compile()
