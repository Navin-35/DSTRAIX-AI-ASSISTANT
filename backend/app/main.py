from fastapi import FastAPI

from app.core.config import settings
from app.api.chat import router as chat_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready GenAI Assistant with Chat, RAG, Memory and Tool Calling"
)


app.include_router(chat_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to DStarix AI Assistant",
        "version": settings.app_version
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.app_name
    }