from app.core.database import AsyncSessionLocal
from app.models.audit_log import AuditLog
from app.core.exceptions import logger


async def save_audit_log(
    *,
    actor: str,
    action: str,
    target_id: int | None = None,
    detail: str | None = None,
) -> None:
    try:
        async with AsyncSessionLocal() as session:
            session.add(AuditLog(actor=actor, action=action, target_id=target_id, detail=detail))
            await session.commit()
    except Exception:
        logger.exception("[AuditLog 저장 실패] actor=%s action=%s", actor, action)