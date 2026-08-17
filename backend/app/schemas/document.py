from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    message: str
    file_name: str
    store_name: str


class DocumentQueryRequest(BaseModel):
    question: str
    store_name: str