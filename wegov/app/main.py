from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.core.exceptions import lifespan, db_exception_handler, global_exception_handler

from app.routers import auth, checkin, checkout, records, workers, sites, notices, schedules, correction, stats

app = FastAPI(
    title="WeGov 출입기록 API",
    description="반도체 협력업체 현장 근로자 출입 기록 관리 시스템",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 설정 — 개발: *, 프로덕션: .env의 CORS_ORIGINS에 허용 URL 지정
origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(SQLAlchemyError, db_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

@app.get("/health", tags=["상태"])
async def health():
    return {"status": "ok"}


@app.get("/health", tags=["상태"])
async def health():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(checkin.router)
app.include_router(checkout.router)
app.include_router(records.router)
app.include_router(workers.router)
app.include_router(sites.router)
app.include_router(notices.router)
app.include_router(schedules.router)
app.include_router(correction.router)
app.include_router(stats.router)
