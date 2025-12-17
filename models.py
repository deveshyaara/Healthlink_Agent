"""
Pydantic models for API request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "patient-12345",
                "message": "What should I eat for better blood sugar control?",
                "thread_id": "thread-abc-123"
            }
        }
    )
    
    user_id: str = Field(..., description="Unique identifier for the patient/user")
    message: str = Field(..., description="User's message/question")
    thread_id: Optional[str] = Field(None, description="Optional thread ID for conversation continuity")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "response": "Based on your Type 2 Diabetes diagnosis, I recommend...",
                "user_id": "patient-12345",
                "thread_id": "thread-abc-123",
                "patient_context": {
                    "name": "John Doe",
                    "age": 45,
                    "medical_history": "Type 2 Diabetes"
                }
            }
        }
    )
    
    response: str = Field(..., description="AI-generated response")
    user_id: str = Field(..., description="User ID from request")
    thread_id: str = Field(..., description="Thread ID for conversation tracking")
    patient_context: Optional[dict] = Field(None, description="Patient context used for response generation")


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str
    message: str
    version: str
