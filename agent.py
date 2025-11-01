import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List
import operator

# --- Load Environment Variables ---
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph import END, StateGraph 

# --- Initialize the LLM (Free Tier) ---
# --- THIS LINE IS THE FIX ---
# Switched to the universally stable name for the newest free model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
)
# ---

# -----------------
# 1. DEFINE THE AGENT STATE
# -----------------
class AgentState(TypedDict):
    input: str
    intent: str
    context: dict
    suggestion: str
    escalate: bool
    chat_history: List[AnyMessage]

# -----------------
# 2. DEFINE THE MOCK FUNCTIONS (Simulating External Systems)
# -----------------

def mock_recognize_intent(query: str) -> str:
    """Mock function for Step 1: Ingestion node"""
    print(f"--- Node: receive_query ---")
    print(f"Recognizing intent for: {query}")
    if "suggestion" in query.lower() or "tip" in query.lower():
        return "suggestion_request"
    elif "explain" in query.lower() or "what is" in query.lower():
        return "info_request"
    else:
        return "general_chat"

def mock_load_context(patient_id: str, intent: str) -> dict:
    """Mock function for Step 2: Context Builder"""
    print(f"--- Node: fetch_context ---")
    print(f"Fetching context for Patient ID: {patient_id} (Intent: {intent})")
    return {
        "patient_id": patient_id,
        "name": "Jane Doe",
        "recent_visit": "2025-10-28",
        "diagnosis": "Type 2 Diabetes",
        "medication": "Metformin 500mg",
        "lab_results": {"hba1c": "7.2%"}
    }

def mock_create_provider_task(context: dict, suggestion: str):
    """Mock function for Step 5: Human-in-the-Loop"""
    print(f"--- Node: escalate_if_needed (ACTION) ---")
    print(f"!!! ESCALATION TRIGGERED !!!")
    print(f"Task created for provider: Review suggestion for {context.get('name')}")
    print(f"Suggestion: {suggestion}")

# -----------------
# 3. DEFINE THE LANGGRAPH NODES
# -----------------

def receive_query(state: AgentState):
    """Node 1: Ingestion"""
    query = state["input"]
    intent = mock_recognize_intent(query)
    
    return {
        "intent": intent,
        "chat_history": state["chat_history"] + [HumanMessage(content=query)]
    }

def fetch_context(state: AgentState):
    """Node 2: Context Builder"""
    patient_id = "patient-123" 
    intent = state["intent"]
    context = mock_load_context(patient_id, intent)
    
    return {"context": context}

def llm_suggest(state:AgentState):
    """Node 3: Reasoning/LLM Node"""
    print(f"--- Node: llm_suggest ---")
    context = state["context"]
    history = state["chat_history"]

    prompt = f"""
    You are an AI Communicator for a health platform. You are talking to a patient.
    Your tone must be empathetic, clear, and supportive. DO NOT give medical advice,
    but you can provide suggestions based on the data.
    
    Patient Context:
    - Name: {context.get('name')}
    - Diagnosis: {context.get('diagnosis')}
    - Medication: {context.get('medication')}
    - Recent HbA1c: {context.get('lab_results', {}).get('hba1c')}

    Respond to the user's last message.
    """
    
    messages = [SystemMessage(content=prompt)] + history
    
    response = llm.invoke(messages)
    suggestion = response.content
    
    return {
        "suggestion": suggestion,
        "chat_history": state["chat_history"] + [AIMessage(content=suggestion)]
    }

def escalate_if_needed(state: AgentState):
    """Node 4 & 5: Suggestion & Human-in-the-Loop Check"""
    print(f"--- Node: escalate_if_needed (Check) ---")
    suggestion = state["suggestion"]
    
    escalation_keywords = ["medication change", "severe pain", "urgent", "dosage"]
    
    if any(keyword in suggestion.lower() for keyword in escalation_keywords):
        context = state["context"]
        mock_create_provider_task(context, suggestion)
        return {"escalate": True}
        
    return {"escalate": False}

def save_and_respond(state: AgentState):
    """Node 6: Response Node"""
    print(f"--- Node: save_and_respond ---")
    suggestion = state["suggestion"]
    
    print(f"Saving to DB (mock): {suggestion}")
    print(f"---")
    print(f"Final Response to User: {suggestion}")
    print(f"---")
    
    return {"input": None}

# -----------------
# 4. DEFINE THE GRAPH
# -----------------
print("Compiling agent graph...")
workflow = StateGraph(AgentState) 

# Add the nodes
workflow.add_node("receive_query", receive_query)
workflow.add_node("fetch_context", fetch_context)
workflow.add_node("llm_suggest", llm_suggest)
workflow.add_node("escalate_if_needed", escalate_if_needed)
workflow.add_node("save_and_respond", save_and_respond)

# Define the edges (the flow)
workflow.set_entry_point("receive_query")
workflow.add_edge("receive_query", "fetch_context") 
workflow.add_edge("fetch_context", "llm_suggest")
workflow.add_edge("llm_suggest", "escalate_if_needed")
workflow.add_edge("escalate_if_needed", "save_and_respond")
workflow.add_edge("save_and_respond", END)

# Compile the graph
app = workflow.compile()

# -----------------
# 5. RUN THE AGENT (as a script)
# -----------------
if __name__ == "__main__":
    print("Agent compiled. Running test...")

    config = {"configurable": {"thread_id": "test-thread-1"}}
    query = "Hi, can you give me a suggestion for my diet?"

    for event in app.stream({"input": query, "chat_history": []}, config):
        for key, value in event.items():
            print(f"Event: {key}")
