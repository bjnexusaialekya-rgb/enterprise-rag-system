import logging
from sqlalchemy import text
from app.database.connection import SessionLocal

logger = logging.getLogger(__name__)


def get_user_role(user_id: str) -> str:
    db = SessionLocal()
    try:
        result = db.execute(
            text("SELECT role FROM users WHERE user_id = :uid"),
            {"uid": user_id}
        ).fetchone()
        if result:
            return result[0]
        # Unknown user defaults to employee
        return "employee"
    finally:
        db.close()


def get_allowed_departments(role: str) -> list[str]:
    db = SessionLocal()
    try:
        rows = db.execute(
            text("SELECT department FROM role_permissions WHERE role = :role"),
            {"role": role}
        ).fetchall()
        return [r[0] for r in rows]
    finally:
        db.close()


def check_access(user_id: str, department: str) -> tuple[bool, str]:
    role = get_user_role(user_id)
    allowed = get_allowed_departments(role)

    if department in allowed:
        logger.info(f"[rbac] ALLOWED — user={user_id} role={role} dept={department}")
        return True, role

    logger.warning(f"[rbac] DENIED — user={user_id} role={role} dept={department} allowed={allowed}")
    return False, role
