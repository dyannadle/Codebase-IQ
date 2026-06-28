from pydantic import BaseModel, Field
from typing import List

class ChatRequest(BaseModel):
    query: str = Field(..., description="The natural language query from the user.")
    repository_ids: List[str] = Field(..., description="List of UUIDs representing the repositories to search.")
