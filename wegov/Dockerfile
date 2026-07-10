FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc musl-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.12-slim

# pyc 파일 생성 금지 → /usr/local 쓰기 시도 차단 (appuser 권한 문제 해결)
# 로그 버퍼링 끔 → 컨테이너 로그 즉시 출력
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

RUN adduser --disabled-password --no-create-home appuser \
    && chown -R appuser:appuser /app \
    && pip uninstall -y pip

USER appuser

EXPOSE 8000
# 컨테이너 시작 시 Alembic이 DB를 최신 마이그레이션 상태로 업데이트한 뒤 FastAPI 서버를 실행한다.
# Git Pull 등으로 새 마이그레이션 파일을 받은 후 이미지를 재빌드(docker compose up --build)하면,
# CMD에 포함된 `alembic upgrade head`가 자동 실행되어 아직 적용되지 않은 마이그레이션이 DB에 적용된다.
# 수동으로 마이그레이션만 실행하려면:
# docker compose run --rm api alembic upgrade head
# 단일 컨테이너 운영 기준. 스케일 아웃(2대 이상) 시에는
# CMD에서 alembic을 제거하고 CI/CD 파이프라인 별도 스텝으로 분리할 것.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers ${WORKERS:-4}"]