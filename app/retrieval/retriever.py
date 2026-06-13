import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

import logging
from typing import Optional
from sqlalchemy import text
from app.database.connection import SessionLocal
from app.ingestion.embedder import embed_text
from app.retrieval.reranker import rerank

logger = logging.getLogger(__name__)


def retrieve(
    query: str,
    department: Optional[str] = None,
    top_k: int = 5,
    semantic_weight: float = 0.6,
    bm25_weight: float = 0.4,
) -> list[dict]:
    if not query or not query.strip():
        raise ValueError("Query must be a non-empty string.")

    logger.info(f"[retriever] Query: '{query}' | Department: {department} | Top-K: {top_k}")

    query_vector = embed_text(query)
    vector_str = "[" + ",".join(str(x) for x in query_vector) + "]"

    dept_clause = "AND d.department = :department" if department else ""

    sql = text(f"""
    WITH semantic AS (
        SELECT
            c.id,
            c.content,
            c.document_id,
            ROW_NUMBER() OVER (ORDER BY c.embedding <=> CAST(:vector AS vector)) AS rank
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE 1=1 {dept_clause}
        ORDER BY c.embedding <=> CAST(:vector AS vector)
        LIMIT 50
    ),
    bm25 AS (
        SELECT
            c.id,
            c.content,
            c.document_id,
            ROW_NUMBER() OVER (
                ORDER BY ts_rank(c.content_tsv, plainto_tsquery('english', :query)) DESC
            ) AS rank
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE c.content_tsv @@ plainto_tsquery('english', :query) {dept_clause}
        ORDER BY ts_rank(c.content_tsv, plainto_tsquery('english', :query)) DESC
        LIMIT 50
    ),
    rrf AS (
        SELECT
            COALESCE(s.id, b.id)                     AS id,
            COALESCE(s.content, b.content)            AS content,
            COALESCE(s.document_id, b.document_id)    AS document_id,
            (
                COALESCE(:sem_w / (60.0 + s.rank), 0) +
                COALESCE(:bm25_w / (60.0 + b.rank), 0)
            )                                          AS rrf_score
        FROM semantic s
        FULL OUTER JOIN bm25 b ON s.id = b.id
    )
    SELECT
        r.id,
        r.content,
        r.document_id,
        d.filename,
        d.department,
        r.rrf_score
    FROM rrf r
    JOIN documents d ON r.document_id = d.id
    ORDER BY r.rrf_score DESC
    LIMIT 20;
    """)

    params = {
        "vector": vector_str,
        "query": query,
        "sem_w": semantic_weight,
        "bm25_w": bm25_weight,
    }
    if department:
        params["department"] = department

    db = SessionLocal()
    try:
        rows = db.execute(sql, params).fetchall()
        candidates = [
            {
                "chunk_id":    str(row[0]),
                "content":     row[1],
                "document_id": str(row[2]),
                "filename":    row[3],
                "department":  row[4],
                "score":       float(row[5]),
            }
            for row in rows
        ]
        logger.info(f"[retriever] RRF candidates: {len(candidates)}")

        reranked = rerank(query=query, chunks=candidates, top_n=top_k)
        return reranked

    except Exception as e:
        logger.error(f"[retriever] Query failed: {e}")
        raise

    finally:
        db.close()
