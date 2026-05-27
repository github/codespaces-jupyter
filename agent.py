import os
import json
import requests
from typing import TypedDict, Annotated, List, Union
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings # Or Google embeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Configuration
API_URL = os.getenv("ENGINE_API_URL", "http://localhost:8080/simulate")

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The messages in the conversation"]
    metrics: Dict[str, Any]

@tool
def simulate_market(beta: float = 0.01, kappa: float = 0.1, lambda_cosmo: float = 0.1):
    """
    Triggers the Quantum-Relativistic simulation for BTC-USD using the specified 
    physical constants. Returns T+1 boundaries and current system stability metrics.
    """
    payload = {
        "beta": beta,
        "kappa": kappa,
        "lambda_cosmo": lambda_cosmo,
        "num_states": 4,
        "lyapunov_threshold": 4.20,
        "lambda_meta": 0.05
    }
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"API call failed with status {response.status_code}"}

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash") # Or vertex ai

# Setup Vector Store (ChromaDB)
# Note: In production, this would be persistent
vector_store = Chroma(
    collection_name="topological_states",
    embedding_function=OpenAIEmbeddings() # Placeholder
)

def call_model(state: AgentState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Quantitative Physicist specializing in Quantum-Relativistic Market Dynamics. "
                   "Your task is to analyze the market using topological metrics (Norm deformation, Chaos limits, Lyapunov exponents). "
                   "Translate these physical properties into actionable financial strategies. "
                   "Always refer to the 'metric deformation' and 'Hilbert space stability' in your analysis."),
        MessagesPlaceholder(variable_name="messages"),
    ])
    chain = prompt | llm.bind_tools([simulate_market])
    response = chain.invoke(state)
    return {"messages": [response]}

def tool_node(state: AgentState):
    tool_messages = []
    last_message = state["messages"][-1]
    for tool_call in last_message.tool_calls:
        tool_result = simulate_market.invoke(tool_call["args"])
        tool_messages.append(ToolMessage(
            content=json.dumps(tool_result),
            tool_call_id=tool_call["id"]
        ))
        
        # RAG: Store the state in ChromaDB
        vector_store.add_texts(
            texts=[f"State: {json.dumps(tool_result['current_state'])} | Prediction: {json.dumps(tool_result['t_plus_1'])}"],
            metadatas=[{"timestamp": "now"}] # Simplify for example
        )
        
    return {"messages": tool_messages}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

app = workflow.compile()

if __name__ == "__main__":
    # Test run
    inputs = {"messages": [HumanMessage(content="Analyze the market with beta=0.02")]}
    for output in app.stream(inputs):
        print(output)
