import time
from pathlib import Path

from google import genai

from app.core.config import settings


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


MODEL_NAME = "gemini-3.6-flash"

_embedding_model = "models/gemini-embedding-2"


def create_file_search_store(
    display_name: str
):
    """
    Create a Gemini File Search store.
    """

    store = client.file_search_stores.create(
        config={
            "display_name": display_name,
            "embedding_model": _embedding_model
        }
    )

    return store


def upload_document(
    file_path: str,
    store_name: str,
    display_name: str
):
    """
    Upload a document directly into
    an existing Gemini File Search store.
    """

    operation = client.file_search_stores.upload_to_file_search_store(
        file=file_path,
        file_search_store_name=store_name,
        config={
            "display_name": display_name
        }
    )

    while not operation.done:

        time.sleep(2)

        operation = client.operations.get(
            operation
        )

    return operation


def ask_document(
    question: str,
    store_name: str
):
    """
    Ask a question using Gemini File Search.
    """

    interaction = client.interactions.create(
        model=MODEL_NAME,
        input=question,
        tools=[
            {
                "type": "file_search",
                "file_search_store_names": [
                    store_name
                ]
            }
        ]
    )

    return interaction
def list_documents(store_name: str):
    """
    Return all documents currently stored
    inside the specified File Search store.
    """

    documents = []

    for document in client.file_search_stores.documents.list(
        parent=store_name
    ):
        documents.append(
            {
                "name": document.name,
                "display_name": getattr(
                    document,
                    "display_name",
                    None
                )
            }
        )

    return documents