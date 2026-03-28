import pymongo
from .config import settings


def get_mongo_client() -> pymongo.MongoClient:
    if not settings.mongo_uri:
        raise ValueError("MONGO_URI is not set")

    client = pymongo.MongoClient(
        settings.mongo_uri,
        appname="cohere-mongodb-rag-fastapi",
    )

    ping_result = client.admin.command("ping")
    if ping_result.get("ok") != 1.0:
        raise ConnectionError("MongoDB ping failed")

    return client


def get_collection():
    client = get_mongo_client()
    db = client.get_database(settings.db_name)
    return db.get_collection(settings.collection_name)


def get_conversation_collection():
    client = get_mongo_client()
    db = client.get_database(settings.db_name)
    return db.get_collection("conversations")
