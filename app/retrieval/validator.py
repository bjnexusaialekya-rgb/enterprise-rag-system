import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.75"))
MINIMUM_CHUNKS = 1


class ValidationError(Exception):
    pass


def validate(
    query: str,
    chunks: list[dict],
    threshold: float = RELEVANCE_THRESHOLD,
    min_chunks: int = MINIMUM_CHUNKS,
) -> list[dict]:
    if not chunks:
        logger.warning(f"[validator] REJECTED — no chunks returned for query: '{query}'")
        raise ValidationError(
            "No relevant documents found. "
            "Cannot generate a response without supporting evidence."
        )

    top_score = chunks[0]["score"]
    logger.info(f"[validator] Top chunk score: {top_score:.4f} | Threshold: {threshold}")

    if top_score < threshold:
        logger.warning(
            f"[validator] REJECTED — top score {top_score:.4f} below "
            f"threshold {threshold} for query: '{query}'"
        )
        raise ValidationError(
            f"Retrieved documents do not meet the relevance threshold "
            f"({top_score:.4f} < {threshold}). "
            f"Cannot generate a reliable response."
        )

    passing = [c for c in chunks if c["score"] >= threshold]

    if len(passing) < min_chunks:
        logger.warning(
            f"[validator] REJECTED — only {len(passing)} chunks passed threshold "
            f"(minimum {min_chunks}) for query: '{query}'"
        )
        raise ValidationError(
            f"Insufficient evidence: {len(passing)} chunk(s) met the relevance bar, "
            f"minimum required is {min_chunks}."
        )

    logger.info(
        f"[validator] PASSED — {len(passing)}/{len(chunks)} chunks accepted "
        f"for query: '{query}'"
    )
    return passing


def safe_validate(
    query: str,
    chunks: list[dict],
    threshold: float = RELEVANCE_THRESHOLD,
) -> tuple[Optional[list[dict]], Optional[str]]:
    try:
        validated = validate(query, chunks, threshold)
        return validated, None
    except ValidationError as e:
        return None, str(e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=== Test 1: Empty chunks (should reject) ===")
    try:
        validate("what is AI?", [])
    except ValidationError as e:
        print(f"REJECTED: {e}\n")

    print("=== Test 2: Low score (should reject) ===")
    low_chunks = [{"chunk_id": "1", "content": "...", "score": 0.016,
                   "filename": "doc.txt", "document_id": "x", "department": "general"}]
    try:
        validate("what is AI?", low_chunks)
    except ValidationError as e:
        print(f"REJECTED: {e}\n")

    print("=== Test 3: High score (should pass) ===")
    high_chunks = [{"chunk_id": "1", "content": "AI is artificial intelligence.",
                    "score": 0.85, "filename": "doc.txt",
                    "document_id": "x", "department": "general"}]
    result = validate("what is AI?", high_chunks)
    print(f"PASSED: {len(result)} chunk(s) accepted\n")

    print("=== Test 4: safe_validate (no exception) ===")
    chunks, err = safe_validate("what is AI?", low_chunks)
    print(f"chunks={chunks} | error='{err}'")
