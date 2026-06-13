import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODE = os.getenv("EMBEDDING_MODE", "local")

if EMBEDDING_MODE == "local":
    from sentence_transformers import SentenceTransformer
    _model = SentenceTransformer('all-MiniLM-L6-v2')
    EMBEDDING_DIM = 384
else:
    from openai import OpenAI
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    EMBEDDING_DIM = 3072


def embed_text(text: str) -> List[float]:
    if EMBEDDING_MODE == "local":
        return _model.encode(text).tolist()
    else:
        response = _client.embeddings.create(
            model="text-embedding-3-large",
            input=text
        )
        return response.data[0].embedding


def embed_texts(texts: List[str]) -> List[List[float]]:
    return [embed_text(t) for t in texts]


def embed_chunks(chunks: List[dict]) -> List[dict]:
    for chunk in chunks:
        chunk["embedding"] = embed_text(chunk["content"])
    return chunks