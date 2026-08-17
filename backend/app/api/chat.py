from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest, ChatResponse

from app.services.llm_service import (
    generate_response,
    stream_chat_response
)

from app.memory.conversation import conversation_memory


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


# ============================================================
# STREAMING CHAT
# ============================================================

@router.post("/stream")
async def stream_chat(request: ChatRequest):

    try:

        # Get previous conversation history
        history = conversation_memory.get_history(
            request.conversation_id
        )


        async def generate():

            full_response = ""

            try:

                # IMPORTANT:
                # stream_chat_response is a normal generator,
                # therefore use "for", not "async for".

                for chunk in stream_chat_response(
                    request.message,
                    history
                ):

                    full_response += chunk

                    yield chunk


                # ------------------------------------------------
                # Save conversation AFTER streaming is complete
                # ------------------------------------------------

                conversation_memory.add_message(
                    request.conversation_id,
                    "user",
                    request.message
                )

                conversation_memory.add_message(
                    request.conversation_id,
                    "assistant",
                    full_response
                )


            except Exception as e:

                print(
                    f"Streaming error: {e}"
                )

                yield (
                    f"\n[ERROR] {str(e)}"
                )


        return StreamingResponse(
            generate(),
            media_type="text/plain"
        )


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# NORMAL CHAT
# ============================================================

@router.post(
    "/",
    response_model=ChatResponse
)
async def chat(request: ChatRequest):

    try:

        # ----------------------------------------------------
        # Get conversation history
        # ----------------------------------------------------

        history = conversation_memory.get_history(
            request.conversation_id
        )


        # ----------------------------------------------------
        # Generate response
        # ----------------------------------------------------

        response = generate_response(
            request.message,
            history
        )


        # ----------------------------------------------------
        # Save user message
        # ----------------------------------------------------

        conversation_memory.add_message(
            request.conversation_id,
            "user",
            request.message
        )


        # ----------------------------------------------------
        # Save assistant response
        # ----------------------------------------------------

        conversation_memory.add_message(
            request.conversation_id,
            "assistant",
            response
        )


        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        return ChatResponse(
            response=response,
            conversation_id=request.conversation_id
        )


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# CLEAR CONVERSATION
# ============================================================

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
        "message":
            "Conversation cleared successfully",

        "conversation_id":
            conversation_id
    }