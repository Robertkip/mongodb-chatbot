from fastapi import FastAPI, HTTPException

from .config import settings
from .models import ChatRequest, ChatResponse, IngestResponse
from .db import get_mongo_client
from .rag import chat_with_rag, ingest_documents

app = FastAPI(title="Cohere MongoDB RAG API", version="1.0.0")


@app.get("/health")
def health():
    try:
        client = get_mongo_client()
        ping = client.admin.command("ping")
        return {
            "status": "ok",
            "mongodb": ping,
            "db_name": settings.db_name,
            "collection_name": settings.collection_name,
            "vector_index_name": settings.vector_index_name,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/ingest", response_model=IngestResponse)
def ingest(limit: int | None = None):
    try:
        inserted_count = ingest_documents(limit)
        return IngestResponse(
            inserted_count=inserted_count,
            dataset_limit=limit or settings.dataset_limit,
            collection=settings.collection_name,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = chat_with_rag(request.message)
        return ChatResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
