from fastapi import FastAPI

from app.api.chat import router as chat_router


app = FastAPI(
    title="DSTRAIX AI Assistant",
    description="AI Assistant API",
    version="1.0.0"
)


app.include_router(chat_router)


@app.get("/")
async def root():
    return {
        "message": "DSTRAIX AI Assistant is running"
    }