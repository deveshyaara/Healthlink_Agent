"""
LangGraph implementation for healthcare chatbot with patient context
"""
import os
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv

from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()

# -----------------
# 1. DEFINE THE AGENT STATE
# -----------------
class AgentState(TypedDict):
    """
    State object that flows through the graph nodes.
    Contains all data needed for personalized medical responses.
    """
    messages: List[AnyMessage]  # Conversation history
    user_id: str  # Patient/user identifier
    patient_context: Dict[str, Any]  # Fetched patient data (name, age, medical history, etc.)
    response: str  # Final AI response


# -----------------
# 2. CONTEXT FETCHER NODE
# -----------------
def fetch_patient_context(state: AgentState) -> Dict[str, Any]:
    """
    Node 1: Fetch patient data from Supabase (database) and Ethereum (blockchain)
    
    This node retrieves personalized patient information to provide context-aware responses.
    """
    print(f"--- Node: fetch_patient_context ---")
    user_id = state["user_id"]
    print(f"Fetching context for user: {user_id}")
    
    patient_context = {}
    
    try:
        # ============================================
        # SUPABASE DATABASE QUERY
        # ============================================
        # TODO: Replace with actual Supabase client initialization
        # from supabase import create_client, Client
        # supabase_url = os.getenv("SUPABASE_URL")
        # supabase_key = os.getenv("SUPABASE_KEY")
        # supabase: Client = create_client(supabase_url, supabase_key)
        # 
        # # Query patient basic info from Supabase
        # response = supabase.table("patients").select("*").eq("user_id", user_id).execute()
        # if response.data:
        #     patient_data = response.data[0]
        #     patient_context["name"] = patient_data.get("name")
        #     patient_context["age"] = patient_data.get("age")
        #     patient_context["email"] = patient_data.get("email")
        #     patient_context["phone"] = patient_data.get("phone")
        
        # MOCK DATA (Remove when implementing actual Supabase)
        patient_context["name"] = "Jane Doe"
        patient_context["age"] = 45
        patient_context["email"] = "jane.doe@example.com"
        print(f"✓ Fetched basic info from Supabase (mocked)")
        
        # ============================================
        # ETHEREUM BLOCKCHAIN QUERY
        # ============================================
        # TODO: Replace with actual Web3 setup
        # from web3 import Web3
        # 
        # # Connect to Ethereum node (Infura, Alchemy, or local node)
        # web3_provider_url = os.getenv("WEB3_PROVIDER_URL")
        # w3 = Web3(Web3.HTTPProvider(web3_provider_url))
        # 
        # # Load smart contract
        # contract_address = os.getenv("CONTRACT_ADDRESS")
        # contract_abi = [...]  # Your contract ABI
        # contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        # 
        # # Fetch medical records from blockchain
        # medical_records = contract.functions.getPatientRecords(user_id).call()
        # patient_context["medical_history"] = medical_records.get("history")
        # patient_context["diagnoses"] = medical_records.get("diagnoses")
        # patient_context["medications"] = medical_records.get("medications")
        # patient_context["allergies"] = medical_records.get("allergies")
        # patient_context["last_visit"] = medical_records.get("last_visit")
        # patient_context["blockchain_hash"] = medical_records.get("record_hash")
        
        # MOCK DATA (Remove when implementing actual Web3)
        patient_context["medical_history"] = "Type 2 Diabetes diagnosed in 2020"
        patient_context["diagnoses"] = ["Type 2 Diabetes", "Hypertension"]
        patient_context["medications"] = ["Metformin 500mg twice daily", "Lisinopril 10mg daily"]
        patient_context["allergies"] = ["Penicillin"]
        patient_context["last_visit"] = "2025-12-01"
        patient_context["blockchain_hash"] = "0x1234567890abcdef..."
        print(f"✓ Fetched medical records from Ethereum (mocked)")
        
    except Exception as e:
        print(f"❌ Error fetching patient context: {e}")
        # Provide minimal fallback context
        patient_context = {
            "name": "Patient",
            "age": "Unknown",
            "medical_history": "No data available",
            "error": str(e)
        }
    
    print(f"Patient context assembled: {patient_context.get('name', 'Unknown')}, Age {patient_context.get('age', 'N/A')}")
    
    return {"patient_context": patient_context}


# -----------------
# 3. CHATBOT NODE (LLM Response Generation)
# -----------------
def generate_response(state: AgentState) -> Dict[str, Any]:
    """
    Node 2: Generate personalized medical response using LLM
    
    This node constructs a dynamic system prompt with patient context and generates
    a personalized response using GPT-4 or similar model.
    """
    print(f"--- Node: generate_response ---")
    
    patient_context = state["patient_context"]
    messages = state["messages"]
    
    # Extract patient details
    name = patient_context.get("name", "Patient")
    age = patient_context.get("age", "Unknown")
    medical_history = patient_context.get("medical_history", "No medical history available")
    diagnoses = ", ".join(patient_context.get("diagnoses", []))
    medications = ", ".join(patient_context.get("medications", []))
    allergies = ", ".join(patient_context.get("allergies", ["None known"]))
    
    # ============================================
    # CONSTRUCT DYNAMIC SYSTEM PROMPT
    # ============================================
    system_prompt = f"""You are a helpful and empathetic medical assistant AI. 

You are currently speaking to **{name}**, who is **{age} years old**.

**Patient Medical Context:**
- **Medical History:** {medical_history}
- **Current Diagnoses:** {diagnoses or "None on record"}
- **Current Medications:** {medications or "None on record"}
- **Known Allergies:** {allergies}

**Important Guidelines:**
1. Provide personalized advice based on the patient's specific medical context
2. Always be empathetic and supportive in your tone
3. DO NOT provide medical diagnoses or prescribe medications
4. If the question requires immediate medical attention, advise the patient to contact their healthcare provider
5. Reference their specific conditions and medications when relevant
6. Be clear that you are an AI assistant and not a replacement for professional medical advice

Answer the patient's question based on their medical context while following these guidelines."""

    # ============================================
    # INITIALIZE LLM
    # ============================================
    try:
        # Initialize Google Gemini LLM (Primary)
        llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Alternative: Use OpenAI (if preferred)
        # from langchain_openai import ChatOpenAI
        # llm = ChatOpenAI(
        #     model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
        #     temperature=0.3,
        #     openai_api_key=os.getenv("OPENAI_API_KEY")
        # )
        
        # Construct full message history with system prompt
        full_messages = [SystemMessage(content=system_prompt)] + messages
        
        # Invoke LLM
        print(f"Invoking LLM with {len(full_messages)} messages...")
        response = llm.invoke(full_messages)
        ai_response = response.content
        
        print(f"✓ Generated response ({len(ai_response)} characters)")
        
        # Update messages with AI response
        updated_messages = messages + [AIMessage(content=ai_response)]
        
        return {
            "messages": updated_messages,
            "response": ai_response
        }
        
    except Exception as e:
        print(f"❌ Error generating response: {e}")
        error_response = "I apologize, but I'm having trouble processing your request right now. Please try again or contact your healthcare provider if this is urgent."
        
        return {
            "messages": messages + [AIMessage(content=error_response)],
            "response": error_response
        }


# -----------------
# 4. BUILD THE LANGGRAPH
# -----------------
def create_healthcare_agent() -> StateGraph:
    """
    Creates and compiles the LangGraph workflow for the healthcare chatbot.
    
    Flow: START -> fetch_patient_context -> generate_response -> END
    """
    print("Building healthcare agent graph...")
    
    # Initialize the graph with AgentState
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("fetch_patient_context", fetch_patient_context)
    workflow.add_node("generate_response", generate_response)
    
    # Define the flow
    workflow.set_entry_point("fetch_patient_context")
    workflow.add_edge("fetch_patient_context", "generate_response")
    workflow.add_edge("generate_response", END)
    
    # Compile the graph
    app = workflow.compile()
    
    print("✓ Healthcare agent graph compiled successfully")
    return app


# -----------------
# 5. INITIALIZE THE AGENT (Module-level)
# -----------------
# This creates a single instance that can be imported by the FastAPI app
healthcare_agent = create_healthcare_agent()


# -----------------
# 6. HELPER FUNCTION FOR EASY INVOCATION
# -----------------
def invoke_agent(user_id: str, message: str, thread_id: str = None) -> Dict[str, Any]:
    """
    Helper function to invoke the healthcare agent.
    
    Args:
        user_id: Patient/user identifier
        message: User's question/message
        thread_id: Optional thread ID for conversation tracking
        
    Returns:
        Dictionary containing response and metadata
    """
    try:
        # Prepare config with thread ID
        config = {"configurable": {"thread_id": thread_id or f"thread-{user_id}"}}
        
        # Prepare initial state
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "user_id": user_id,
            "patient_context": {},
            "response": ""
        }
        
        # Invoke the agent
        print(f"\n{'='*60}")
        print(f"INVOKING AGENT for user: {user_id}")
        print(f"{'='*60}")
        
        final_state = healthcare_agent.invoke(initial_state, config)
        
        print(f"{'='*60}")
        print(f"AGENT INVOCATION COMPLETE")
        print(f"{'='*60}\n")
        
        return {
            "response": final_state.get("response", ""),
            "user_id": user_id,
            "thread_id": config["configurable"]["thread_id"],
            "patient_context": final_state.get("patient_context", {})
        }
        
    except Exception as e:
        print(f"❌ Error invoking agent: {e}")
        raise


# -----------------
# 7. TEST THE AGENT (Optional, for standalone testing)
# -----------------
if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING HEALTHCARE AGENT")
    print("="*60 + "\n")
    
    # Test case
    test_result = invoke_agent(
        user_id="patient-12345",
        message="What should I eat for better blood sugar control?",
        thread_id="test-thread-001"
    )
    
    print("\n" + "="*60)
    print("TEST RESULT:")
    print("="*60)
    print(f"Response: {test_result['response']}")
    print(f"User ID: {test_result['user_id']}")
    print(f"Thread ID: {test_result['thread_id']}")
    print("="*60 + "\n")
