# WeGov 백엔드 개발 가이드

## 프로젝트 개요
반도체 협력업체 현장 근로자 출입 기록 FastAPI 백엔드.
Python 3.12 / FastAPI 0.111.0 / SQLAlchemy 2.0.30 async / PostgreSQL 16

## API 엔드포인트

| 메서드 | 경로 | 설명 | 인증 | 역할 |
|---|---|---|---|---|
| GET | /health | 서버 상태 확인 | 불필요 | — |
| POST | /auth/login | 로그인 (이름+생년월일8자리+비밀번호) → role+name+worker_id 반환 | 불필요 | — |
| POST | /auth/activate | 계정 최초 활성화 (주민번호) | 불필요 | — |
| POST | /auth/refresh | Refresh Token으로 Access Token 갱신 (자동 로그인) | 불필요 | — |
| POST | /auth/change-password | 개인 비밀번호 변경 | 필요 | 전체 |
| PATCH | /auth/default-password | 역할별 초기 비밀번호 설정 | 필요 | admin |
| POST | /checkin/manual | 수동 입실 | 필요 | 전체 |
| POST | /checkin/from-schedule | 스케줄 기반 자동 입실 | 필요 | 전체 |
| GET | /checkin/today-schedule | 오늘 스케줄 조회 | 필요 | 전체 |
| GET | /checkin/realtime | 실시간 입실 현황 | 필요 | leader+ |
| POST | /checkout | 퇴실 | 필요 | 전체 |
| GET | /records/me | 내 출입기록 조회 | 필요 | 전체 |
| GET | /records/worker/{id} | 특정 직원 기록 조회 | 필요 | leader+ |
| GET | /workers | 재직자 목록 | 필요 | leader+ |
| GET | /workers/{id} | 직원 상세 조회 | 필요 | leader+ |
| POST | /workers | 직원 등록 | 필요 | admin |
| POST | /workers/bulk | 직원 일괄 등록 (CSV/엑셀) — 등록 즉시 역할별 초기 비밀번호 자동 세팅 | 필요 | admin |
| PATCH | /workers/{id} | 직원 수정 | 필요 | admin |
| PATCH | /workers/{id}/reinstate | 복직 처리 + 비밀번호 초기화 | 필요 | admin |
| DELETE | /workers/{id} | 직원 퇴사 처리 (soft delete) | 필요 | admin |
| GET | /sites | 사업장 목록 | 필요 | 전체 |
| POST | /sites | 사업장 등록 | 필요 | admin |
| PATCH | /sites/{id} | 사업장 수정 | 필요 | admin |
| DELETE | /sites/{id} | 사업장 삭제 | 필요 | admin |
| GET | /schedules/me | 내 스케줄 조회 | 필요 | 전체 |
| GET | /schedules/worker/{id} | 특정 직원 스케줄 조회 | 필요 | leader+ |
| POST | /schedules | 스케줄 등록 (건별) | 필요 | admin |
| POST | /schedules/bulk | CSV 스케줄 일괄 업로드 | 필요 | admin |
| DELETE | /schedules/{id} | 스케줄 삭제 | 필요 | admin |
| GET | /notices | 공지사항 목록 | 필요 | 전체 |
| POST | /notices | 공지사항 등록 | 필요 | admin |
| PATCH | /notices/{id} | 공지사항 수정 | 필요 | admin |
| DELETE | /notices/{id} | 공지사항 삭제 | 필요 | admin |
| POST | /corrections | 수정 요청 등록 | 필요 | 전체 |
| GET | /corrections/me | 내 수정 요청 목록 | 필요 | 전체 |
| GET | /corrections/pending | 승인 대기 목록 | 필요 | leader+ |
| POST | /corrections/{id}/resolve | 승인/반려 | 필요 | admin |
| GET | /stats/by-process | 공정별 통계 | 필요 | leader+ |
| GET | /stats/by-site | 사업장별 통계 | 필요 | leader+ |
| GET | /stats/by-worker | 작업자별 통계 | 필요 | leader+ |
| GET | /stats/excel | 엑셀 다운로드 | 필요 | leader+ |
| POST | /messages | 메시지 전송 | 필요 | 전체 |
| GET | /messages/me | 받은 메시지 목록 | 필요 | 전체 |
| GET | /messages/thread/{id} | 특정 상대 대화 내역 | 필요 | 전체 |
| PATCH | /messages/{id}/read | 메시지 읽음 처리 | 필요 | 전체 |
| GET | /process-contracts | 공정별 계약시간 목록 | 필요 | 전체 |
| GET | /process-contracts/lookup | 사업장+공정+라인 단건 조회 (GET /processes로 대체 가능) | 필요 | 전체 |
| POST | /process-contracts | 계약시간 등록 | 필요 | admin |
| DELETE | /process-contracts/{id} | 계약시간 삭제 | 필요 | admin |
| GET | /processes | 사업장별 공정 목록 조회 | 필요 | 전체 |

## 모델 목록

| 파일 | 테이블 | 역할 |
|---|---|---|
| worker.py | workers | 근로자 |
| work_record.py | work_records | 출입기록 |
| site.py | sites | 사업장 |
| schedule.py | schedules | 근무 스케줄 |
| worker_document.py | worker_documents | 근로자 서류 |
| notice.py | notices | 공지사항 |
| correction.py | corrections | 수정 요청 |
| audit_log.py | audit_logs | 감사 로그 |
| message.py | messages | 엑스티톡 채팅 메시지 |
| process_contract.py | process_contracts | 공정별 계약 작업시간 |

## 핵심 설계 결정

### 인증 / 보안
- JWT sub: `str(worker.id)` 값 사용, 토큰에 `iat`(발급 시각) 포함
- Access Token 유효시간: 120분 (기본값)
- Refresh Token 유효시간: 30일 — `POST /auth/refresh`로 갱신
- 로그인 응답: `access_token`, `refresh_token`, `worker_id`, `name`, `role` 반환
- **아이디**: 이름 + birth_date(8자리, yyyymmdd 형식)
- **비밀번호 형식**: worker/leader = 숫자 4자리, admin/최종관리자 = 8자 이상 (문자+숫자+특수문자)
- **역할별 초기 비밀번호**: password_hash가 없으면 환경변수 초기값(`DEFAULT_PASSWORD_WORKER` / `DEFAULT_PASSWORD_ADMIN`)으로 로그인
- 직원 등록·복직 시 역할에 맞는 초기 비밀번호 자동 세팅
- 개인 비밀번호 변경: `POST /auth/change-password` — 현재 비밀번호 확인 후 변경
- `token_invalidated_at`: 퇴직·역할 변경 시 이 시각 기록 → 이전 발급 토큰 즉시 차단
- `get_current_user` 반환 타입: `(sub: str, iat: int | None)` 튜플
- `get_current_worker` 반환 타입: Worker 객체 — 모든 인증 필요 엔드포인트에서 사용 (is_active + token_invalidated_at 동시 체크)
- `/auth/refresh`: payload의 `type == "refresh"` 클레임 검증 — access_token으로 갱신 시도 차단
- `/auth/activate`: 동명이인 시 `scalars().first()` 사용 — 500 에러 방지
- 모든 라우터에서 `get_current_user` 완전 제거 — `get_current_worker`로 통일
- `POST /messages`: `receiver_id` 생략 가능 — 생략 시 is_final_admin=True 관리자에게 자동 전송
- `POST /checkin/from-schedule`: `shift_type` 파라미터 추가 — 스케줄 기반 입실 시 근무표 직접 선택 가능

### 역할 접근 제어
- `require_admin` / `require_leader_or_above` (app/core/deps.py)
  - admin: 직원·사업장 등록·수정·삭제, 수정 요청 승인, 공정 계약시간 관리, 스케줄 관리
  - leader+: 직원 목록·상세, 타직원 기록·스케줄, 통계, 수정 대기 목록, 실시간 현황
  - 전체: 본인 기록·스케줄·공지·수정 요청·채팅·공정 계약시간 조회
- `is_final_admin`: admin 중 최상위 최종관리자 여부 (최대 3명)

### 데이터 무결성
- SQLAlchemy 2.0 async 스타일 (`async with session`)
- Worker 조회: `select(Worker).where(Worker.id == id, Worker.active_filter())`
- Worker 물리 삭제 금지 — `is_active=False` soft delete만
- WorkRecord 물리 삭제 금지 — `is_voided=True` soft delete만
- `duration_minutes`: PostgreSQL STORED Computed 컬럼 — checkout 후 `await db.refresh(record)` 필수
- GPS 미적용 — 사용자가 직접 사업장·공정 선택하는 방식

### 입력값 검증 (Literal)
- `role`: worker / leader / admin
- `shift_type`: D / S / O / 주 / 야
- `correction_type`: CHECKIN_MISS / CHECKOUT_MISS / WRONG_PRESS / LONG_STAY
- `status`(재직상태): 재직 / 수습 / 수습해지 / 퇴사예정 / 휴직 / 입사예정 / 신입 / 퇴사
- `work_status`(업무진행상태): 입사교육완료 / 수습진행중 / 수습완료 / 퇴사예정 / 정상근무

### 출입기록 관련
- 지각 판정: RecordResponse.is_late — KST 기준, 근무표별 기준시각(D/주=06:00, S/야=18:00, O=08:00)
- is_voided=True 기록은 모든 조회 API에서 자동 제외
- round(회차): 날짜 기준 is_voided 제외 카운트 + 1

### Worker 필드
- 기본: name, company, phone, role, status, work_status, team, group_name, squad, line
- 인증: birth_date(아이디용 8자리 yyyymmdd), password_hash(개인 비밀번호 bcrypt), resident_number_hash(주민번호 bcrypt)
- 추가: employee_number(사번), email, english_name, outsourcing_company, probation_end_date, contract_end_date, contract_renewal_date, is_final_admin, token_invalidated_at

### 공정별 계약시간
- process_contracts 테이블 (112건 시드 데이터)
- `/processes?site_name=` — 사업장별 공정 목록 전용 API
- `/processes?site_name=` — 공정 목록 + 계약시간 한 번에 조회. 입실 시 선택한 row의 contract_hours를 저장해두면 퇴실 알람 타이머로 사용 가능 (별도 lookup 호출 불필요)

### 조직도 역할 매핑 (엑스티 조직도 DB 기준)
- emp → worker, hr → leader, admin → admin
- 최종관리자(Y) → is_final_admin=True (최대 3명)

### 감사 로그
- `save_audit_log()` — 직원 등록·수정·퇴사, 수정 요청 승인·반려 시 audit_logs 기록

### 테스트 데이터
- `scripts/seed.py` — 사업장 8개·직원 10명·출입기록·스케줄
- `scripts/seed_process_contracts.py` — 공정별 계약시간 112건
- 실행: `docker compose -f docker-compose.dev.yml exec -e PYTHONPATH=/app api python /app/scripts/<파일명>`
- 테스트 계정: 김관리/19800101(admin), 박리더/19850215(leader), 최현장/19900510(worker) — 아이디=이름, 비밀번호=역할별 초기값
- 테스트 주민번호: 김관리=8001011234561, 최현장=9005101234561

## 환경변수

| 변수 | 설명 |
|---|---|
| DATABASE_URL | PostgreSQL 접속 URL (asyncpg 형식 필수) |
| JWT_SECRET_KEY | JWT 서명 키 |
| JWT_ALGORITHM | HS256 |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | 토큰 만료 시간(분) — 기본값: 120 |
| CORS_ORIGINS | 허용 출처 (쉼표 구분, 개발: *) |
| DEFAULT_PASSWORD_WORKER | worker/leader 역할 초기 비밀번호 (숫자 4자리) |
| DEFAULT_PASSWORD_ADMIN | admin/최종관리자 역할 초기 비밀번호 (8자 이상) |

## 배포

- 프로덕션: Railway
  - URL: https://sat-production-0f30.up.railway.app
  - docs: https://sat-production-0f30.up.railway.app/docs
- 개발 실행: `docker compose -f docker-compose.dev.yml up`
- 마이그레이션 생성(개발): `docker compose -f docker-compose.dev.yml run --rm api alembic revision --autogenerate -m "설명"`
- 마이그레이션 적용(개발): `docker compose -f docker-compose.dev.yml exec api alembic upgrade head`
- 마이그레이션 적용(프로덕션): Railway 배포 시 Dockerfile CMD에서 자동 실행
