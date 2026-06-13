import os
import logging
import cohere
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))


def rerank(query: str, chunks: list[dict], top_n: int = 5) -> list[dict]:
    if not chunks:
        return []

    documents = [c["content"] for c in chunks]

    response = client.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=documents,
        top_n=top_n
    )

    reranked = []
    for hit in response.results:
        chunk = chunks[hit.index].copy()
        chunk["score"] = round(hit.relevance_score, 4)
        reranked.append(chunk)

    logger.info(f"[reranker] Top score: {reranked[0]['score']} | Chunks reranked: {len(reranked)}")
    return reranked
