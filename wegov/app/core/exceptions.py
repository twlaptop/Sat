from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from sqlalchemy.exc import SQLAlchemyError
import logging
import logging.handlers
import queue
import os
import asyncio

ENV = os.getenv("ENV", "production").lower().strip()

formatter = logging.Formatter(
    "[%(asctime)s] [PID:%(process)d] %(levelname)s → %(message)s"
)

logger = logging.getLogger("wegov")
logger.setLevel(logging.DEBUG if ENV != "production" else logging.ERROR)

if ENV == "production":
    # 루트 로거에 위임 → 인프라 수집기 통합 수집
    # formatter는 Uvicorn 기본 포맷으로 출력됨 (인지하고 넘어가는 트레이드오프)
    logger.propagate = True
    listener = None
else:
    # 개발: RichHandler 직결 (콘솔) + FileHandler 큐 처리 (파일)
    logger.propagate = False
    from rich.logging import RichHandler
    rich_handler = RichHandler(rich_tracebacks=True)
    logger.addHandler(rich_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        "wegov.log", maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    log_queue = queue.Queue()
    queue_handler = logging.handlers.QueueHandler(log_queue)
    listener = logging.handlers.QueueListener(log_queue, file_handler)
    logger.addHandler(queue_handler)


class SafeBackgroundTasks(BackgroundTasks):
    """
    [사용 규칙]
    1. 함수 인자에 반드시 핵심 식별자(worker_id, record_id 등) 포함
    2. DB 작업 시 라우터 세션 넘기지 말 것 → AsyncSessionLocal()로 새 세션 직접 열기
    3. 함수 내부 except: logger.error (한 줄 요약) + raise
       → 전체 스택 트레이스는 SafeBackgroundTasks가 한 번만 기록
    """
    def add_task(self, func, *args, **kwargs):
        async def wrapped():
            try:
                if asyncio.iscoroutinefunction(func):
                    await func(*args, **kwargs)
                else:
                    func(*args, **kwargs)
            except Exception:
                logger.exception("[BackgroundTask 오류] %s", func.__name__)
        super().add_task(wrapped)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if listener:
        listener.start()
    yield
    if listener:
        listener.stop()


async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("[DB 오류] %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "데이터베이스 오류가 발생했습니다."})


async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return await http_exception_handler(request, exc)
    logger.exception("[서버 오류] %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "서버 오류가 발생했습니다."})