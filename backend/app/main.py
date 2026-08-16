from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.agent import router as agent_router


app = FastAPI(
    title="DSTRAIX AI Assistant",
    description="Intelligent AI Assistant with Chat, RAG and Tools",
    version="1.0.0"
)


app.include_router(
    chat_router
)

app.include_router(
    documents_router
)

app.include_router(
    agent_router
)


@app.get("/")
async def root():

    return {
        "message": "DSTRAIX AI Assistant is running",
        "version": "1.0.0"
    }