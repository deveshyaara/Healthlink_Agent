"""
FastAPI Backend for Healthcare Chatbot
Production-ready API with LangGraph integration
"""
import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from models import ChatRequest, ChatResponse, HealthCheckResponse
from agent_graph import invoke_agent

# Load environment variables
load_dotenv()

# -----------------
# FASTAPI APP INITIALIZATION
# -----------------
app = FastAPI(
    title="Healthcare Chatbot API",
    description="Production-ready backend for personalized healthcare chatbot with blockchain integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# -----------------
# CORS MIDDLEWARE
# -----------------
# Configure CORS for Next.js frontend
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://yourdomain.com").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Modify this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------
# ERROR HANDLERS
# -----------------
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# -----------------
# HEALTH CHECK ENDPOINT
# -----------------
@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify API is running.
    Useful for load balancers and monitoring systems.
    """
    return HealthCheckResponse(
        status="healthy",
        message="Healthcare Chatbot API is running",
        version="1.0.0"
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Healthcare Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# -----------------
# MAIN CHAT ENDPOINT
# -----------------
@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Main chat endpoint that processes user messages and returns personalized responses.
    
    This endpoint:
    1. Receives user_id and message from the frontend
    2. Fetches patient context from Supabase and Ethereum
    3. Generates a personalized medical response using LLM
    4. Returns the AI response with metadata
    
    Args:
        request (ChatRequest): Contains user_id, message, and optional thread_id
        
    Returns:
        ChatResponse: AI-generated response with patient context
        
    Raises:
        HTTPException: If validation fails or agent invocation encounters an error
    """
    try:
        # Validate request
        if not request.user_id or not request.user_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id is required and cannot be empty"
            )
        
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="message is required and cannot be empty"
            )
        
        # Generate thread_id if not provided
        thread_id = request.thread_id or f"thread-{request.user_id}-{uuid.uuid4().hex[:8]}"
        
        # Log incoming request
        print(f"\n{'='*60}")
        print(f"[{datetime.utcnow().isoformat()}] Incoming Chat Request")
        print(f"User ID: {request.user_id}")
        print(f"Thread ID: {thread_id}")
        print(f"Message: {request.message}")
        print(f"{'='*60}\n")
        
        # Invoke the LangGraph agent
        result = invoke_agent(
            user_id=request.user_id,
            message=request.message,
            thread_id=thread_id
        )
        
        # Prepare response
        response = ChatResponse(
            response=result["response"],
            user_id=result["user_id"],
            thread_id=result["thread_id"],
            patient_context=result.get("patient_context")
        )
        
        # Log response
        print(f"\n{'='*60}")
        print(f"[{datetime.utcnow().isoformat()}] Chat Response Sent")
        print(f"User ID: {response.user_id}")
        print(f"Response Length: {len(response.response)} characters")
        print(f"{'='*60}\n")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        # Log error
        print(f"\n{'='*60}")
        print(f"[{datetime.utcnow().isoformat()}] ERROR in /chat endpoint")
        print(f"Error: {str(e)}")
        print(f"{'='*60}\n")
        
        # Return error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}"
        )


# -----------------
# PATIENT CONTEXT ENDPOINT (Optional)
# -----------------
@app.get("/patient/{user_id}", tags=["Patient"])
async def get_patient_context(user_id: str):
    """
    Retrieve patient context without generating a response.
    Useful for frontend to display patient info or debugging.
    
    Args:
        user_id: Patient/user identifier
        
    Returns:
        Patient context dictionary
    """
    try:
        if not user_id or not user_id.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id is required"
            )
        
        # Import the fetch function
        from agent_graph import fetch_patient_context
        
        # Fetch context
        state = {"user_id": user_id}
        result = fetch_patient_context(state)
        
        return {
            "user_id": user_id,
            "patient_context": result["patient_context"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch patient context: {str(e)}"
        )


# -----------------
# CONVERSATION HISTORY ENDPOINT (Optional - requires implementation)
# -----------------
@app.get("/chat/history/{user_id}", tags=["Chat"])
async def get_chat_history(user_id: str, limit: int = 10):
    """
    Retrieve chat history for a user.
    
    TODO: Implement conversation history storage and retrieval
    This would require a database or cache to store conversation history.
    
    Args:
        user_id: Patient/user identifier
        limit: Number of messages to retrieve (default: 10)
        
    Returns:
        List of previous messages
    """
    # This is a placeholder - implement with your database
    return {
        "user_id": user_id,
        "message": "Chat history endpoint not yet implemented",
        "todo": "Implement conversation history storage (PostgreSQL, MongoDB, or Redis)"
    }


# -----------------
# RUN THE SERVER
# -----------------
if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment variables
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    print(f"\n{'='*60}")
    print(f"Starting Healthcare Chatbot API")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Docs: http://{host}:{port}/docs")
    print(f"{'='*60}\n")
    
    uvicorn.run(
        "backend_api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
