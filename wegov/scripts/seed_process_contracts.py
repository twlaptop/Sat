"""
공정별 계약시간 데이터 삽입 스크립트
출처: 공정별 사업장 위치 및 작업시간_주소삭제.xlsx

실행:
  docker compose -f docker-compose.dev.yml exec -e PYTHONPATH=/app api python /app/scripts/seed_process_contracts.py
"""
import asyncio, re, sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.database import DATABASE_URL
from app.models.process_contract import ProcessContract

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)

# (site_name, process, line, hours_str)
RAW = [
    ("삼성전자 온양사업장", "AVI", "1L", "6.7시간"),
    ("삼성전자 온양사업장", "AVI", "2L", "6.7시간"),
    ("삼성전자 온양사업장", "AVI", "3L", "6.7시간"),
    ("삼성전자 온양사업장", "AVI", "4L", "6.7시간"),
    ("삼성전자 온양사업장", "AVI", "C동", "6.7시간"),
    ("삼성전자 천안사업장", "AVI", "C2", "3.4시간"),
    ("삼성전자 온양사업장", "BackLap", "1L", "3시간"),
    ("삼성전자 온양사업장", "BackLap", "2L", "3시간"),
    ("삼성전자 온양사업장", "BackLap", "3L", "3시간"),
    ("삼성전자 온양사업장", "BackLap", "4L", "3시간"),
    ("삼성전자 온양사업장", "BackLap", "5L", "3시간"),
    ("삼성전자 온양사업장", "Bellows, Fan 교체", "2L", "약 2시간"),
    ("삼성전자 온양사업장", "Bellows, Fan 교체", "3L", "약 2시간"),
    ("삼성전자 온양사업장", "Bellows, Fan 교체", "4L", "약 2시간"),
    ("삼성전자 온양사업장", "Bellows, Fan 교체", "5L", "약 2시간"),
    ("삼성전자 천안사업장", "Belt교체", "C1", "약 2시간"),
    ("삼성전자 천안사업장", "BLADE", "C1", "7시간"),
    ("삼성전자 온양사업장", "CarrierBox", "C동", "7시간"),
    ("삼성전자 온양사업장", "ChillerExpender", "1L", "2시간"),
    ("삼성전자 온양사업장", "ChillerExpender", "2L", "1시간"),
    ("삼성전자 온양사업장", "ChillerExpender", "3L", "3시간"),
    ("삼성전자 온양사업장", "ChillerExpender", "4L", "6시간"),
    ("삼성전자 온양사업장", "ChillerExpender", "5L", "7시간"),
    ("삼성전자 천안사업장", "COW", "C1", "7시간"),
    ("삼성전자 온양사업장", "Cure", "2L", "3.5시간"),
    ("하나마이크론", "Deflux PM", "하나마이크론", "약 4.5시간"),
    ("삼성전자 온양사업장", "Die Attach", "1L", "6.5시간"),
    ("삼성전자 온양사업장", "Die Attach", "3L", "6.5시간"),
    ("삼성전자 온양사업장", "Die Attach", "4L", "6.5시간"),
    ("삼성전자 온양사업장", "Die Attach", "5L", "6.5시간"),
    ("IMK", "FCM JIG(2L)", "2L", None),
    ("IMK", "FCM JIG(5L)", "5L", None),
    ("삼성전자 온양사업장", "Feeder", "C", "6~8시간"),
    ("삼성전자 천안사업장", "Feeder", "C1", "6시간"),
    ("삼성전자 천안사업장", "FINISH", "C1", "약 6시간"),
    ("삼성전자 온양사업장", "FlowCure", "2L", "약 3.5시간"),
    ("삼성전자 온양사업장", "FlowCure", "5L", "2시간"),
    ("삼성전자 천안사업장", "FluxCleaner", "C1", "3시간"),
    ("하나마이크론", "JigMZ", "하나마이크론", None),
    ("삼성전자 천안사업장", "LAMI", "C1", "7시간"),
    ("삼성전자 온양사업장", "Module", "C동", "10시간"),
    ("삼성전자 온양사업장", "Module Router", "C동", "2.5시간"),
    ("삼성전자 온양사업장", "Mold", "2L", "10시간"),
    ("삼성전자 온양사업장", "Mold", "4L", "10시간"),
    ("삼성전자 온양사업장", "MP Packing", "1L", "6.5시간"),
    ("삼성전자 온양사업장", "MP Packing", "2L", "6.5시간"),
    ("삼성전자 온양사업장", "MP Packing", "3L", "6.5시간"),
    ("삼성전자 온양사업장", "MP Packing", "4L", "6.5시간"),
    ("삼성전자 온양사업장", "MP Packing", "5L", "6.5시간"),
    ("삼성전자 천안사업장", "MP Packing", "C2", "6.5시간"),
    ("삼성전자 천안사업장", "MPGA TEST", "C4", "2시간"),
    ("삼성전자 온양사업장", "Overhaul", "1L", "약 6.5시간"),
    ("삼성전자 온양사업장", "Overhaul", "2L", "약 6.5시간"),
    ("삼성전자 온양사업장", "Overhaul", "3L", "약 6.5시간"),
    ("삼성전자 온양사업장", "Overhaul", "4L", "약 6.5시간"),
    ("삼성전자 천안사업장", "Overhaul", "C2", "약 6.5시간"),
    ("삼성전자 온양사업장", "Packing", "C동", "2시간"),
    ("삼성전자 온양사업장", "PCB Loader", "1L", "1시간"),
    ("삼성전자 온양사업장", "PCB Loader", "2L", "1시간"),
    ("삼성전자 온양사업장", "PCB Loader", "3L", "1시간"),
    ("삼성전자 온양사업장", "PCB Loader", "4L", "1시간"),
    ("삼성전자 온양사업장", "PCB Loader", "5L", "1시간"),
    ("삼성전자 온양사업장", "Plasma", "1L", "1시간"),
    ("삼성전자 온양사업장", "Plasma", "3L", "1시간"),
    ("삼성전자 온양사업장", "Plasma", "4L", "2시간"),
    ("삼성전자 온양사업장", "Plasma", "5L", "2시간"),
    ("삼성전자 천안사업장", "Plasma (CBM)", "C1", "5시간"),
    ("SKHynix 청주사업장", "Reflow", "SKHynix", "7시간"),
    ("삼성전자 천안사업장", "Reflow10", "C5", "7시간"),
    ("삼성전자 천안사업장", "Reflow10", "C1", "7시간"),
    ("삼성전자 온양사업장", "Reflow5", "5L", "5.5시간"),
    ("삼성전자 온양사업장", "Reflow6", "1L", "5시간"),
    ("삼성전자 온양사업장", "Reflow6", "2L", "5시간"),
    ("삼성전자 천안사업장", "Reflow6", "C1", "5시간"),
    ("삼성전자 온양사업장", "Reflow6", "C동", "6시간"),
    ("인팩일렉스", "Reflow9", "수원", "약 6시간"),
    ("삼성전자 온양사업장", "Router", "C동", "2시간"),
    ("삼성전자 온양사업장", "Saw&Sorter", "2L", "3시간"),
    ("삼성전자 온양사업장", "Saw&Sorter", "3L", "3시간"),
    ("삼성전자 온양사업장", "Saw&Sorter", "4L", "3시간"),
    ("삼성전자 온양사업장", "Saw&Sorter", "5L", "3시간"),
    ("삼성전자 천안사업장", "Saw&Sorter", "C5", "6시간"),
    ("삼성전자 온양사업장", "SMT", "C동", "6시간"),
    ("삼성전자 온양사업장", "Spindle", "2L", "3시간"),
    ("삼성전자 온양사업장", "Spindle", "3L", "3시간"),
    ("삼성전자 온양사업장", "Spindle", "4L", "3시간"),
    ("삼성전자 온양사업장", "Spindle", "5L", "3시간"),
    ("삼성전자 천안사업장", "S기술", "C1", "약 6.5시간"),
    ("삼성전자 온양사업장", "TEST", "1L", "7시간"),
    ("삼성전자 온양사업장", "TEST", "3L", "7시간"),
    ("삼성전자 온양사업장", "TEST", "4L", "7시간"),
    ("삼성전자 온양사업장", "Underfill", "C동", "4시간"),
    ("삼성전자 온양사업장", "Underfill", "2L", "약 2.5시간"),
    ("삼성전자 온양사업장", "Underfill", "5L", "3시간"),
    ("삼성전자 온양사업장", "Water Jet", "2L", "약 3.5시간"),
    ("삼성전자 천안사업장", "WLM기술", "C1", "약 6.5시간"),
    ("삼성전자 천안사업장", "Wrapping", "C1", "약 3시간"),
    ("삼성전자 천안사업장", "계측설비", "C1", "3시간"),
    ("삼성전자 천안사업장", "계측설비", "C5", "3시간"),
    ("삼성전자 온양사업장", "냉동고", "2L", "2시간"),
    ("삼성전자 온양사업장", "냉동고", "5L", "1시간"),
    ("삼성전자 온양사업장", "릴머지", "C동", "10시간"),
    ("EO테크닉스", "마킹설비", "C1", "5시간"),
    ("EO테크닉스", "마킹설비", "EO테크닉스", "5시간"),
    ("삼성전자 온양사업장", "부대설비", "5L", "2시간"),
    ("삼성전자 천안사업장", "부대설비", "C1", "3시간"),
    ("삼성전자 천안사업장", "부대설비", "C5", "7시간"),
    ("경신", "세척기", "경신", "4.5시간"),
    ("삼성전자 온양사업장", "세척실", "C동", "3시간"),
    ("경신", "집진기", "경신", "2시간"),
    ("IMK", "파트반출", "5L", None),
    ("IMK", "파트반출", "C", None),
]


def parse_hours(hours_str):
    if hours_str is None:
        return None, False
    is_approx = hours_str.startswith("약")
    # 숫자 추출 (6~8시간 같은 범위는 평균값 사용)
    nums = re.findall(r"\d+\.?\d*", hours_str)
    if not nums:
        return None, is_approx
    if len(nums) >= 2 and "~" in hours_str:
        return (float(nums[0]) + float(nums[1])) / 2, True
    return float(nums[0]), is_approx


async def seed():
    async with AsyncSession() as db:
        result = await db.execute(select(ProcessContract).limit(1))
        if result.scalars().first():
            print("공정 계약시간 데이터가 이미 있습니다. 건너뜁니다.")
            return

        print("공정별 계약시간 삽입 중...")
        for site, process, line, hours_str in RAW:
            hours, is_approx = parse_hours(hours_str)
            db.add(ProcessContract(
                site_name=site,
                process=process,
                line=line,
                contract_hours=hours,
                is_approximate=is_approx,
            ))

        await db.commit()
        print(f"✅ 완료! 총 {len(RAW)}건 삽입")


if __name__ == "__main__":
    asyncio.run(seed())
