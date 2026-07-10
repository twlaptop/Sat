from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.process_contract import ProcessContract
from app.schemas.process_contract import ProcessContractCreate, ProcessContractResponse

router = APIRouter(prefix="/process-contracts", tags=["공정별 계약시간"])


@router.get("", response_model=list[ProcessContractResponse], summary="공정별 계약시간 목록 조회")
async def list_process_contracts(
    site_name: str | None = Query(None, description="사업장명 필터"),
    process: str | None = Query(None, description="공정명 필터"),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    stmt = select(ProcessContract).order_by(ProcessContract.site_name, ProcessContract.process)
    if site_name:
        stmt = stmt.where(ProcessContract.site_name == site_name)
    if process:
        stmt = stmt.where(ProcessContract.process == process)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/lookup", response_model=ProcessContractResponse | None, summary="사업장+공정+라인으로 계약시간 단건 조회")
async def lookup_contract(
    site_name: str = Query(...),
    process: str = Query(...),
    line: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    stmt = select(ProcessContract).where(
        ProcessContract.site_name == site_name,
        ProcessContract.process == process,
    )
    if line:
        stmt = stmt.where(ProcessContract.line == line)
    result = await db.execute(stmt)
    return result.scalars().first()


@router.post("", response_model=ProcessContractResponse, status_code=status.HTTP_201_CREATED, summary="공정별 계약시간 등록 (관리자)")
async def create_process_contract(
    body: ProcessContractCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    pc = ProcessContract(**body.model_dump())
    db.add(pc)
    await db.commit()
    await db.refresh(pc)
    return pc


@router.delete("/{pc_id}", status_code=status.HTTP_204_NO_CONTENT, summary="공정별 계약시간 삭제 (관리자)")
async def delete_process_contract(
    pc_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(ProcessContract).where(ProcessContract.id == pc_id))
    pc = result.scalar_one_or_none()
    if pc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="공정 계약시간을 찾을 수 없습니다.")
    await db.delete(pc)
    await db.commit()
