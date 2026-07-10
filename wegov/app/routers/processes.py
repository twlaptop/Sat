from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_worker
from app.models.process_contract import ProcessContract

router = APIRouter(prefix="/processes", tags=["공정 목록"])


@router.get("", summary="사업장별 공정 목록 조회")
async def list_processes(
    site_name: str = Query(..., description="사업장명"),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_worker),
):
    result = await db.execute(
        select(ProcessContract.process, ProcessContract.line, ProcessContract.contract_hours, ProcessContract.is_approximate)
        .where(ProcessContract.site_name == site_name)
        .order_by(ProcessContract.process)
    )
    rows = result.all()
    return [
        {
            "process": r.process,
            "line": r.line,
            "contract_hours": r.contract_hours,
            "is_approximate": r.is_approximate,
        }
        for r in rows
    ]
