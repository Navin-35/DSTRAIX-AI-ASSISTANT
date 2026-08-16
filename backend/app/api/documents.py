import os
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.document import (
    DocumentUploadResponse,
    DocumentQueryRequest
)

from app.services.rag_service import (
    create_file_search_store,
    upload_document,
    ask_document,
    list_documents
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post(
    "/store",
    response_model=dict
)
async def create_store(
    name: str = "DSTRAIX Documents"
):

    try:

        store = create_file_search_store(
            display_name=name
        )

        return {
            "message": "File Search store created",
            "store_name": store.name,
            "display_name": name
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post(
    "/upload",
    response_model=DocumentUploadResponse
)
async def upload_document_endpoint(
    store_name: str,
    file: UploadFile = File(...)
):

    allowed_extensions = {
        ".pdf",
        ".txt",
        ".md",
        ".docx"
    }

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Use PDF, TXT, MD, or DOCX."
            )
        )

    temp_path = None

    try:

        file_content = await file.read()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:

            temp_file.write(file_content)

            temp_path = temp_file.name

        upload_document(
            file_path=temp_path,
            store_name=store_name,
            display_name=file.filename
        )

        return DocumentUploadResponse(
            message="Document uploaded successfully",
            file_name=file.filename,
            store_name=store_name
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if temp_path and os.path.exists(temp_path):

            os.remove(temp_path)


@router.post(
    "/ask"
)
async def ask_document_endpoint(
    request: DocumentQueryRequest
):

    try:

        interaction = ask_document(
            question=request.question,
            store_name=request.store_name
        )

        return {
            "question": request.question,
            "answer": interaction.output_text
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get(
    "/list"
)
async def list_documents_endpoint(
    store_name: str
):

    try:

        documents = list_documents(
            store_name
        )

        return {
            "store_name": store_name,
            "documents": documents,
            "count": len(documents)
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )