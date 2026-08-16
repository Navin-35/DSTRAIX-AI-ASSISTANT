from pydantic import BaseModel, Field


class ChatRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1
    )

    conversation_id: str = Field(
        default="default",
        min_length=1
    )


class ChatResponse(BaseModel):

    response: str

    conversation_id: str


class AgentRequest(BaseModel):

    message: str


class AgentResponse(BaseModel):

    response: str