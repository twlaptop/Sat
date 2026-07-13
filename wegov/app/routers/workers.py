import csv, io
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_admin, require_leader_or_above
from app.core.security import hash_password
from app.core.config import settings
from app.core.audit import save_audit_log
from app.models.worker import Worker
from app.schemas.worker import WorkerCreate, WorkerUpdate, WorkerResponse, WorkerBulkUploadResponse

router = APIRouter(prefix="/workers", tags=["근로자 관리"])


@router.get("", response_model=list[WorkerResponse], summary="재직자 목록 조회")
async def list_workers(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(50, ge=1, le=200, description="페이지당 항목 수"),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_leader_or_above),
):
    offset = (page - 1) * limit
    result = await db.execute(
        select(Worker).where(Worker.active_filter()).order_by(Worker.name).offset(offset).limit(limit)
    )
    return result.scalars().all()


@router.get("/{worker_id}", response_model=WorkerResponse, summary="직원 상세 조회")
async def get_worker(
    worker_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_leader_or_above),
):
    result = await db.execute(
        select(Worker).where(Worker.id == worker_id, Worker.active_filter())
    )
    worker = result.scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="직원을 찾을 수 없습니다.")
    return worker


@router.post("", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED, summary="직원 등록 (관리자)")
async def create_worker(
    body: WorkerCreate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    data = body.model_dump()
    # 주민번호가 평문으로 들어오면 해시 처리
    if data.get("resident_number_hash") and not data["resident_number_hash"].startswith("$2b$"):
        data["resident_number_hash"] = hash_password(data["resident_number_hash"])

    worker = Worker(**data)
    db.add(worker)
    await db.commit()
    await db.refresh(worker)
    await save_audit_log(actor=str(admin.id), action="직원 등록", target_id=worker.id, detail=f"이름: {worker.name}")
    return worker


@router.patch("/{worker_id}", response_model=WorkerResponse, summary="직원 정보 수정 (관리자)")
async def update_worker(
    worker_id: int,
    body: WorkerUpdate,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(Worker).where(Worker.id == worker_id, Worker.active_filter())
    )
    worker = result.scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="직원을 찾을 수 없습니다.")

    changed = list(body.model_dump(exclude_unset=True).keys())
    role_changed = "role" in changed
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(worker, field, value)

    if role_changed:
        worker.token_invalidated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(worker)
    await save_audit_log(actor=str(admin.id), action="직원 정보 수정", target_id=worker.id, detail=f"변경 항목: {', '.join(changed)}")
    return worker


@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT, summary="직원 퇴사 처리 (관리자) — soft delete")
async def deactivate_worker(
    worker_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(Worker).where(Worker.id == worker_id, Worker.active_filter())
    )
    worker = result.scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="직원을 찾을 수 없습니다.")

    worker.is_active = False
    worker.status = "퇴사"
    worker.token_invalidated_at = datetime.now(timezone.utc)
    await db.commit()
    await save_audit_log(actor=str(admin.id), action="직원 퇴사 처리", target_id=worker_id, detail=f"이름: {worker.name}")


@router.patch("/{worker_id}/reinstate", response_model=WorkerResponse, summary="복직 처리 + 비밀번호 초기화 (관리자)")
async def reinstate_worker(
    worker_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    result = await db.execute(
        select(Worker).where(Worker.id == worker_id)
    )
    worker = result.scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="직원을 찾을 수 없습니다.")
    if worker.is_active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 재직 중인 직원입니다.")

    worker.is_active = True
    worker.status = "재직"
    worker.password_hash = None  # 초기 비밀번호로 초기화
    worker.token_invalidated_at = None
    await db.commit()
    await db.refresh(worker)
    await save_audit_log(actor=str(admin.id), action="직원 복직 처리", target_id=worker_id, detail=f"이름: {worker.name}")
    return worker


@router.post("/bulk", response_model=WorkerBulkUploadResponse, status_code=status.HTTP_201_CREATED, summary="직원 일괄 등록 — CSV/엑셀 (관리자)")
async def bulk_create_workers(
    file: UploadFile = File(..., description="CSV 파일 — 헤더: name, company, birth_date, role, employee_number, ..."),
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin),
):
    content = await file.read()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("cp949", errors="replace")

    reader = csv.DictReader(io.StringIO(text))
    required = {"name", "company", "birth_date"}
    if not required.issubset(set(reader.fieldnames or [])):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"CSV 헤더 오류 — 필수 컬럼: {', '.join(required)}",
        )

    created, errors = 0, []
    for i, row in enumerate(reader, start=2):
        try:
            role = row.get("role") or "worker"
            resident_raw = row.get("resident_number_hash") or None
            worker = Worker(
                name=row["name"],
                company=row["company"],
                birth_date=row["birth_date"],
                role=role,
                employee_number=row.get("employee_number") or None,
                phone=row.get("phone") or None,
                team=row.get("team") or None,
                status=row.get("status") or "재직",
                # 개인 비밀번호 미설정 → 역할별 초기값으로 자동 로그인됨
                password_hash=None,
                resident_number_hash=hash_password(resident_raw) if resident_raw else None,
            )
            db.add(worker)
            created += 1
        except Exception as e:
            errors.append({"row": i, "error": str(e)})

    await db.commit()
    return {"created": created, "errors": errors}
