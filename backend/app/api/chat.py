from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import generate_response
from app.memory.conversation import conversation_memory


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post(
    "/",
    response_model=ChatResponse
)
async def chat(request: ChatRequest):

    try:

        history = conversation_memory.get_history(
            request.conversation_id
        )

        response = generate_response(
            request.message,
            history
        )

        conversation_memory.add_message(
            request.conversation_id,
            "user",
            request.message
        )

        conversation_memory.add_message(
            request.conversation_id,
            "assistant",
            response
        )

        return ChatResponse(
            response=response,
            conversation_id=request.conversation_id
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@router.delete(
    "/{conversation_id}",
    status_code=200
)
async def clear_conversation(
    conversation_id: str
):

    conversation_memory.clear_history(
        conversation_id
    )

    return {
        "message": "Conversation cleared successfully",
        "conversation_id": conversation_id
    }        