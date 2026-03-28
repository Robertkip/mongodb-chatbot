from __future__ import annotations

import os
from typing import Any

import cohere
from datasets import load_dataset
import pandas as pd
from tqdm import tqdm

from .config import settings
from .db import get_collection, get_conversation_collection


co = cohere.ClientV2(api_key=settings.cohere_api_key) if settings.cohere_api_key else None


def require_clients() -> None:
    if not settings.cohere_api_key:
        raise ValueError("COHERE_API_KEY is not set")
    if not settings.hf_token:
        raise ValueError("HF_TOKEN is not set")
    if co is None:
        raise ValueError("Cohere client failed to initialize")


def combine_attributes(row: pd.Series) -> str:
    combined = f"{row['company']} {row['sector']} "

    for report in row["reports"]:
        combined += (
            f"{report['year']} {report['title']} {report['author']} {report['content']} "
        )

    for news in row["recent_news"]:
        combined += f"{news['headline']} {news['summary']} "

    return combined.strip()


def get_embedding(text: str, input_type: str) -> list[float]:
    require_clients()

    if not text.strip():
        return []

    response = co.embed(
        model=settings.embed_model,
        input_type=input_type,
        embedding_types=["float"],
        texts=[text],
    )

    return response.embeddings.float_[0]


def load_market_reports_dataset(limit: int | None = None) -> pd.DataFrame:
    require_clients()

    if settings.hf_token:
        os.environ["HF_TOKEN"] = settings.hf_token

    dataset = load_dataset(
        settings.dataset_name,
        split=settings.dataset_split,
        streaming=True,
    )

    size = limit or settings.dataset_limit
    dataset_df = pd.DataFrame(dataset.take(size))
    dataset_df["combined_attributes"] = dataset_df.apply(combine_attributes, axis=1)

    tqdm.pandas(desc="Generating embeddings")
    dataset_df["embedding"] = dataset_df["combined_attributes"].progress_apply(
        lambda text: get_embedding(text, "search_document")
    )
    return dataset_df


def ingest_documents(limit: int | None = None) -> int:
    dataset_df = load_market_reports_dataset(limit)
    collection = get_collection()
    collection.delete_many({})
    documents = dataset_df.to_dict("records")
    result = collection.insert_many(documents)
    return len(result.inserted_ids)


def vector_search(query: str) -> list[dict[str, Any]]:
    collection = get_collection()
    query_embedding = get_embedding(query, "search_query")

    pipeline = [
        {
            "$vectorSearch": {
                "index": settings.vector_index_name,
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": settings.num_candidates,
                "limit": settings.top_k,
            }
        },
        {
            "$project": {
                "_id": 0,
                "company": 1,
                "ticker": 1,
                "sector": 1,
                "combined_attributes": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    return list(collection.aggregate(pipeline))


def build_prompt(query: str, context_docs: list[dict[str, Any]]) -> str:
    context = "\n\n".join(
        [
            f"{doc['company']} ({doc['ticker']}) | sector={doc.get('sector', '')} | score={doc.get('score', 0):.4f}\n{doc['combined_attributes']}"
            for doc in context_docs
        ]
    )

    return f"""
You are an investment research assistant.
Answer the user's question using only the supplied context.
If the context is insufficient, say so plainly.

Context:
{context}

Question:
{query}
""".strip()


def chat_with_rag(query: str) -> dict[str, Any]:
    require_clients()
    context_docs = vector_search(query)
    prompt = build_prompt(query, context_docs)

    response = co.chat(
        model=settings.chat_model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    answer = response.message.content[0].text if response.message.content else "No answer returned."

    conversations = get_conversation_collection()
    conversations.insert_one(
        {
            "user_message": query,
            "retrieved_docs": context_docs,
            "assistant_response": answer,
        }
    )

    return {
        "answer": answer,
        "context": context_docs,
    }
