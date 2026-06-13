import hashlib
import secrets
import logging
from sqlalchemy import text
from app.database.connection import SessionLocal

logger = logging.getLogger(__name__)


def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def generate_api_key(owner: str, role: str = "employee") -> str:
    raw_key = f"rag-{secrets.token_urlsafe(32)}"
    key_hash = _hash_key(raw_key)
    db = SessionLocal()
    try:
        db.execute(
            text("INSERT INTO api_keys (key_hash, owner, role) VALUES (:key_hash, :owner, :role)"),
            {"key_hash": key_hash, "owner": owner, "role": role}
        )
        db.commit()
        logger.info(f"[api_key] Generated key for owner={owner} role={role}")
    finally:
        db.close()
    return raw_key


def validate_api_key(raw_key: str) -> dict | None:
    key_hash = _hash_key(raw_key)
    db = SessionLocal()
    try:
        result = db.execute(
            text("SELECT owner, role, is_active FROM api_keys WHERE key_hash = :key_hash"),
            {"key_hash": key_hash}
        ).fetchone()
        if not result:
            logger.warning("[api_key] INVALID — key not found")
            return None
        owner, role, is_active = result
        if not is_active:
            logger.warning(f"[api_key] INACTIVE — owner={owner}")
            return None
        db.execute(
            text("UPDATE api_keys SET last_used_at = NOW() WHERE key_hash = :key_hash"),
            {"key_hash": key_hash}
        )
        db.commit()
        logger.info(f"[api_key] VALID — owner={owner} role={role}")
        return {"owner": owner, "role": role}
    finally:
        db.close()


def revoke_api_key(owner: str) -> bool:
    db = SessionLocal()
    try:
        db.execute(
            text("UPDATE api_keys SET is_active = FALSE WHERE owner = :owner"),
            {"owner": owner}
        )
        db.commit()
        logger.info(f"[api_key] Revoked all keys for owner={owner}")
        return True
    finally:
        db.close()
