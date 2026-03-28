from pydantic import BaseModel, Field
from typing import Any


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User question")


class ChatResponse(BaseModel):
    answer: str
    context: list[dict[str, Any]]


class IngestResponse(BaseModel):
    inserted_count: int
    dataset_limit: int
    collection: str
