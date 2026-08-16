from fastapi import APIRouter, HTTPException

from app.schemas.chat import (
    AgentRequest,
    AgentResponse
)

from app.services.agent_service import run_agent


router = APIRouter(
    prefix="/agent",
    tags=["Agent"]
)


@router.post(
    "/",
    response_model=AgentResponse
)
async def agent(
    request: AgentRequest
):

    try:

        response = run_agent(
            request.message
        )

        return AgentResponse(
            response=response
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )