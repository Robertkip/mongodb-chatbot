from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    cohere_api_key: str = os.getenv("COHERE_API_KEY", "")
    hf_token: str = os.getenv("HF_TOKEN", "")
    mongo_uri: str = os.getenv("MONGO_URI", "")
    db_name: str = os.getenv("DB_NAME", "asset_management_use_case")
    collection_name: str = os.getenv("COLLECTION_NAME", "market_reports")
    vector_index_name: str = os.getenv("VECTOR_INDEX_NAME", "vector_index")
    embed_model: str = os.getenv("EMBED_MODEL", "embed-v4.0")
    chat_model: str = os.getenv("CHAT_MODEL", "command-r-plus")
    top_k: int = int(os.getenv("TOP_K", "5"))
    num_candidates: int = int(os.getenv("NUM_CANDIDATES", "100"))
    dataset_name: str = os.getenv("DATASET_NAME", "MongoDB/fake_tech_companies_market_reports")
    dataset_split: str = os.getenv("DATASET_SPLIT", "train")
    dataset_limit: int = int(os.getenv("DATASET_LIMIT", "100"))


settings = Settings()
