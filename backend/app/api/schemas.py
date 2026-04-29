from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)

class SQLRequest(BaseModel):
    sql: str = Field(min_length=6, max_length=4000)
