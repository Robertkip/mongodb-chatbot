from app.config import settings
from app.rag import ingest_documents


if __name__ == "__main__":
    inserted_count = ingest_documents(settings.dataset_limit)
    print(
        f"Inserted {inserted_count} documents into "
        f"{settings.db_name}.{settings.collection_name}"
    )
