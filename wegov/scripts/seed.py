"""
개발 환경 테스트 데이터 삽입 스크립트

실행:
  docker compose -f docker-compose.dev.yml run --rm api python scripts/seed.py
"""
import asyncio
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import bcrypt as _bcrypt

def hash_password(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode(), _bcrypt.gensalt()).decode()
from app.models.worker import Worker
from app.models.site import Site
from app.models.work_record import WorkRecord
from app.models.schedule import Schedule
from app.core.database import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)

now = datetime.now(timezone.utc)
yesterday = now - timedelta(days=1)
two_days_ago = now - timedelta(days=2)


SITES = [
    {"name": "삼성전자 온양사업장", "company": "삼성전자"},
    {"name": "삼성전자 천안사업장", "company": "삼성전자"},
    {"name": "SKHynix 청주사업장", "company": "SK하이닉스"},
    {"name": "하나마이크론", "company": "하나마이크론"},
    {"name": "IMK", "company": "IMK"},
    {"name": "EO테크닉스", "company": "EO테크닉스"},
    {"name": "인팩일렉스", "company": "인팩일렉스"},
    {"name": "경신", "company": "경신"},
]

# birth_date: 로그인 비밀번호 (6자리)
# resident: 주민번호 평문 → bcrypt 해시로 저장
WORKERS = [
    {
        "name": "김관리",
        "company": "엑스티",
        "role": "admin",
        "team": "제조3팀",
        "group_name": "제조1그룹",
        "squad": "A조",
        "birth_date": "800101",
        "resident": "8001011234561",
        "status": "재직",
        "gender": "남",
    },
    {
        "name": "박리더",
        "company": "엑스티",
        "role": "leader",
        "team": "제조3팀",
        "group_name": "제조1그룹",
        "squad": "A조",
        "birth_date": "850215",
        "resident": "8502151234561",
        "status": "재직",
        "gender": "남",
    },
    {
        "name": "이리더",
        "company": "엑스티",
        "role": "leader",
        "team": "제조2팀",
        "group_name": "제조2그룹",
        "squad": "B조",
        "birth_date": "870330",
        "resident": "8703302234562",
        "status": "재직",
        "gender": "여",
    },
    {
        "name": "최현장",
        "company": "엑스티",
        "role": "worker",
        "team": "제조3팀",
        "group_name": "제조1그룹",
        "squad": "A조",
        "birth_date": "900510",
        "resident": "9005101234561",
        "status": "재직",
        "gender": "남",
    },
    {
        "name": "정수진",
        "company": "엑스티",
        "role": "worker",
        "team": "제조3팀",
        "group_name": "제조1그룹",
        "squad": "A조",
        "birth_date": "920720",
        "resident": "9207202234562",
        "status": "재직",
        "gender": "여",
    },
    {
        "name": "강민준",
        "company": "엑스티",
        "role": "worker",
        "team": "제조3팀",
        "group_name": "교대직장",
        "squad": "A조",
        "birth_date": "940815",
        "resident": "9408151234561",
        "status": "재직",
        "gender": "남",
    },
    {
        "name": "윤서영",
        "company": "엑스티",
        "role": "worker",
        "team": "제조2팀",
        "group_name": "제조2그룹",
        "squad": "B조",
        "birth_date": "910225",
        "resident": "9102252234562",
        "status": "재직",
        "gender": "여",
    },
    {
        "name": "장동현",
        "company": "엑스티",
        "role": "worker",
        "team": "제조2팀",
        "group_name": "제조2그룹",
        "squad": "B조",
        "birth_date": "930430",
        "resident": "9304301234561",
        "status": "재직",
        "gender": "남",
    },
    {
        "name": "임지현",
        "company": "엑스티",
        "role": "worker",
        "team": "제조1팀",
        "group_name": "제조1그룹",
        "squad": "C조",
        "birth_date": "950615",
        "resident": "9506152234562",
        "status": "재직",
        "gender": "여",
    },
    {
        "name": "한승우",
        "company": "엑스티",
        "role": "worker",
        "team": "제조1팀",
        "group_name": "제조1그룹",
        "squad": "C조",
        "birth_date": "970901",
        "resident": "9709011234561",
        "status": "수습",
        "gender": "남",
    },
]


async def seed():
    async with AsyncSession() as db:
        # ── 이미 시드 데이터가 있으면 건너뜀 ──────────────────────
        result = await db.execute(select(Worker).limit(1))
        if result.scalars().first():
            print("이미 데이터가 있습니다. 건너뜁니다.")
            return

        # ── 1. 사업장 ─────────────────────────────────────────────
        print("사업장 등록 중...")
        sites = []
        for s in SITES:
            site = Site(**s)
            db.add(site)
            sites.append(site)
        await db.flush()

        # ── 2. 직원 ───────────────────────────────────────────────
        print("직원 등록 중...")
        workers = []
        for w in WORKERS:
            resident = w.pop("resident")
            worker = Worker(
                **w,
                resident_number_hash=hash_password(resident),
                is_active=True,
            )
            db.add(worker)
            workers.append(worker)
        await db.flush()

        # ── 3. 출입기록 (이틀치) ──────────────────────────────────
        print("출입기록 등록 중...")
        sample_records = [
            # (worker_idx, site_idx, process, shift_type, 입실 오프셋h, 체류h)
            (3, 0, "4라인 몰드 세정", "D", 8, 9),
            (3, 0, "4라인 몰드 세정", "D", 18, 1),
            (4, 0, "C동 릴머지", "S", 16, 8),
            (5, 0, "2라인 몰드 세정", "D", 8, 8),
            (6, 1, "COW", "주", 8, 9),
            (7, 1, "BLADE", "야", 20, 8),
            (8, 1, "LAMI", "D", 8, 8),
            (9, 1, "FINISH", "D", 8, 4),
        ]

        for day_offset, base_day in [(1, two_days_ago), (0, yesterday)]:
            for w_idx, s_idx, process, shift_type, hour_in, duration_h in sample_records:
                checkin = base_day.replace(hour=hour_in, minute=0, second=0, microsecond=0)
                checkout = checkin + timedelta(hours=duration_h)
                record = WorkRecord(
                    worker_id=workers[w_idx].id,
                    round=1,
                    site_name=sites[s_idx].name,
                    process=process,
                    shift_type=shift_type,
                    checkin_at=checkin,
                    checkout_at=checkout,
                    is_voided=False,
                )
                db.add(record)

        # ── 4. 오늘 스케줄 ────────────────────────────────────────
        print("스케줄 등록 중...")
        today = now.date()
        schedule_data = [
            (3, 0, "4라인 몰드 세정", "D"),
            (4, 0, "C동 릴머지", "S"),
            (5, 0, "2라인 몰드 세정", "D"),
            (6, 1, "COW", "주"),
            (7, 1, "BLADE", "야"),
        ]
        for w_idx, s_idx, process, shift_type in schedule_data:
            schedule = Schedule(
                worker_id=workers[w_idx].id,
                company=sites[s_idx].company,
                site=sites[s_idx].name,
                process=process,
                date=today,
            )
            db.add(schedule)

        await db.commit()
        print("✅ 시드 완료!")
        print(f"  사업장 {len(SITES)}개 / 직원 {len(WORKERS)}명 / 출입기록 {len(sample_records) * 2}건 / 스케줄 {len(schedule_data)}건")
        print()
        print("테스트 계정 (이름 + 생년월일로 로그인):")
        print("  관리자: 김관리 / 800101")
        print("  리더:   박리더 / 850215")
        print("  작업자: 최현장 / 900510")


if __name__ == "__main__":
    asyncio.run(seed())
