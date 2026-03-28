# Cohere + MongoDB RAG FastAPI App

A small FastAPI app that:
- loads the MongoDB market reports demo dataset from Hugging Face
- generates embeddings with Cohere
- stores them in MongoDB Atlas
- answers questions with retrieval-augmented generation (RAG)

## 1) Create a virtualenv

```bash
cd cohere-mongodb-rag-fastapi
python -m venv .venv
source .venv/bin/activate
```

## 2) Install dependencies

```bash
pip install -r requirements.txt
```

## 3) Configure environment

```bash
cp .env.example .env
# then edit .env with your real keys
```

Required values:
- `COHERE_API_KEY`
- `HF_TOKEN`
- `MONGO_URI`

## 4) Create MongoDB Atlas vector index

Create these Atlas resources:
- database: `asset_management_use_case`
- collection: `market_reports`
- vector index name: `vector_index`

Index definition:

```json
{
  "fields": [
    {
      "numDimensions": 1024,
      "path": "embedding",
      "similarity": "cosine",
      "type": "vector"
    }
  ]
}
```

## 5) Ingest data into MongoDB

```bash
python ingest.py
```

## 6) Run the API

```bash
uvicorn app.main:app --reload
```

Open:
- API docs: <http://127.0.0.1:8000/docs>
- Health: <http://127.0.0.1:8000/health>

## Example request

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Which company looks strongest in cloud infrastructure?"}'
```

## Endpoints

- `GET /health` - service status
- `POST /chat` - run RAG against MongoDB + Cohere
- `POST /ingest` - trigger ingestion from the API

## Notes

- Use `search_document` for stored document embeddings.
- Use `search_query` for user query embeddings.
- If `$vectorSearch` fails, confirm the Atlas vector index exists and the dimensions match the embedding model.
