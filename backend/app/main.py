from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.agent import router as agent_router


app = FastAPI(
    title="DSTRAIX AI Assistant",
    description="Intelligent AI Assistant with Chat, RAG and Tools",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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