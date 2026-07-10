from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.site import Site
from app.schemas.site import SiteCreate, SiteUpdate, SiteResponse

router = APIRouter(prefix="/sites", tags=["사업장"])


@router.get("", response_model=list[SiteResponse], summary="사업장 목록 조회")
async def list_sites(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    result = await db.execute(select(Site).order_by(Site.name))
    return result.scalars().all()


@router.post("", response_model=SiteResponse, status_code=status.HTTP_201_CREATED, summary="사업장 등록 (관리자)")
async def create_site(
    body: SiteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    site = Site(**body.model_dump())
    db.add(site)
    await db.commit()
    await db.refresh(site)
    return site


@router.patch("/{site_id}", response_model=SiteResponse, summary="사업장 수정 (관리자)")
async def update_site(
    site_id: int,
    body: SiteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    result = await db.execute(select(Site).where(Site.id == site_id))
    site = result.scalar_one_or_none()
    if site is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사업장을 찾을 수 없습니다.")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(site, field, value)

    await db.commit()
    await db.refresh(site)
    return site


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT, summary="사업장 삭제 (관리자)")
async def delete_site(
    site_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    result = await db.execute(select(Site).where(Site.id == site_id))
    site = result.scalar_one_or_none()
    if site is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사업장을 찾을 수 없습니다.")

    await db.delete(site)
    await db.commit()
