from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Schema for user asking a question about the file."""
    message: str = Field(..., description="User query to ask about the file.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "how many layers are there in the decoder?"
            }
        }
    }


class ChatResponse(BaseModel):
    """Schema for chatbot response to user query."""
    reply: str = Field(..., description="LLM-generated response to the query.")
    session_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the conversation session."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "reply": "The decoder has 6 layers.",
                "session_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    }
