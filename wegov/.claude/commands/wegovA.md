# WeGov 프로젝트 컨텍스트 — 즉시 재개용

이 스킬을 호출한 순간부터 당신은 WeGov 백엔드 개발을 이어받습니다.
아래 내용을 완전히 숙지하고 즉시 작업을 재개하세요.

---

## 프로젝트 개요
삼성전자 사업장 내 공정 라인의 실제 입실·퇴실 시간을 관리하는 반도체 협력업체 현장 근로자 출입 기록 FastAPI 백엔드.
경로: C:\sat\wegov
브랜치: main
Python: 3.12 / Docker Compose v2

스택: FastAPI 0.111.0 / SQLAlchemy 2.0.30 async / asyncpg
      PostgreSQL 16 / Alembic 1.13.1 / python-jose / passlib[bcrypt] / pydantic-settings 2.2.1

### 핵심 요구사항 (슬라이드 12 기준)
1. 입실 직전·퇴실 직후 버튼 1회로 시간 자동 저장
2. GPS 기반 위치 확인 및 공정 선택
3. 하루 여러 번 출입하는 회차별 기록 관리
4. 작업자별 총 라인 작업시간 자동 계산
5. 작업자별 공정 투입횟수·공정별 작업시간 집계
6. 누락·오입력 수정 요청 및 관리자 승인 절차
7. 실시간 입실현황, 이상기록 알림, 엑셀 다운로드
8. 개인정보·위치정보 수집 범위 제한 및 이력 보존

### 개발 우선순위
① 버튼 입력 → ② 회차별 시간 계산 → ③ 공정별 집계 → ④ 예외처리 → ⑤ 통계·엑셀 출력

---

## 2026-07-01 미팅 확정 사항

### 사업장 구조 (6개 근무지)
| 사업장 | 동/건물 |
|---|---|
| 천안(온양) | C동(C1~C4), P동(P1~P4) — 삼성전자 |
| 언양 | 1동~4동, C동(부속) — 삼성전자 |
| 청주 | 청주 이공장 — SK하이닉스 |

### 라인 코드 전체
COW / BLADE / LAMI / FINISH / 4L Mold / 2L Mold / Reel Merge / Module / Carrier Box

### 조 구조
- 제조2팀: A/B/C/D조 (COW → BLADE/LAMI/FINISH)
- 제조3팀: A/B/C조 + Day·Swing·OFFICE

### 공정 시간 체계
- 공정 약 40개, 분(min) 단위 고정값 (예: 200분, 250분, 257분)
- 퇴실 알람 기준으로 사용
- **추가 요청 필요** — 개발팀이 요청했으나 의뢰처가 명확히 제공하겠다고 답하지 않음

### 이석 처리
- 나올 때 1번, 들어올 때 1번만 누르면 됨
- 이석 사유는 퇴근 후 일괄 입력 가능

### 로그인 방식
- 이름 + 생년월일 6자리 (예: 950110)
- 조직도에 없는 사람 자동 차단
- 테스트용 초기 데이터는 가명 처리 (김땡1, 김땡2 등 — 개인정보법)

### 앱 분리
- 작업자: 모바일 앱 (C파트 담당자 제작 예정, 받아올 예정)
- 관리자: 웹만 (별도 모바일 앱 없음)

### 신규 기능 추가 확정
- 퇴실 알람: 공정 계약 시간 경과 시 핸드폰 알림
- 공지사항: 관리자 공지 → 작업자 앱 알림 (SOP 변경 공지 주 용도)

---

## DB 스키마 요약

### workers 테이블
| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | BigInt PK | 자동증가 |
| name | String(100) | 이름 (NOT NULL) |
| company | String(100) | 회사명 (NOT NULL) |
| phone | String(50) | 전화번호 (nullable) |
| role | String(20) | worker/leader/admin (default: worker) |
| status | String(20) | 재직/수습/수습해지/퇴사예정/휴직/입사예정/신입/퇴사 (default: 입사예정) |
| work_status | String(20) | 업무진행상태 — 정상근무/수습진행중 (nullable) |
| team | String(50) | 팀 — 제조1팀/제조2팀/제조3팀/경영지원팀 (nullable) |
| group_name | String(50) | 그룹 — 제조1그룹/제조2그룹/교대직장 등 (nullable) |
| squad | String(20) | 조 — A조/B조/C조/D조/Day·Swing·OFFICE 등 (nullable) |
| line | String(50) | 라인 — COW/BLADE/LAMI/FINISH/4L Mold/Reel Merge/Module/2L Mold/Carrier Box 등 (nullable) |
| birth_date | String(6) | 생년월일 6자리 — 로그인 비밀번호 역할 (예: 950110) |
| resident_number_hash | String | 주민번호 bcrypt 해시 — 최초 계정 활성화용 |
| expected_hire_date | Date | 입사예정일 (nullable) |
| blood_type | String(5) | 혈액형 (nullable) |
| gender | String(10) | 성별 (nullable) |
| job_title | String(100) | 직무 (nullable) |
| profile_image_url | String | 프로필 사진 URL (nullable) |
| is_active | Boolean | 재직 여부 (soft delete) |
| version | Integer | 낙관적 잠금 |
| created_at | DateTime(tz) | 등록 시각 |

**유니크 인덱스**: (company, phone) WHERE phone IS NOT NULL

**계정 활성화 흐름**: 작업자 앱 최초 접속 → 주민번호 입력 → resident_number_hash 대조 → 일치 시 활성화 → 이후 이름+birth_date로 로그인

### work_records 테이블
| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | BigInt PK | 자동증가 |
| worker_id | BigInt FK | workers.id (CASCADE DELETE) |
| round | Integer | 회차 (NOT NULL) — 하루 몇 번째 입실인지 |
| site_name | String(100) | 사업장명 — 사용자가 직접 선택 (NOT NULL) |
| process | String(100) | 공정명 — 사용자가 직접 선택 (NOT NULL) |
| shift_type | String(10) | 근무표 유형 — D/S/O/주/야 (NOT NULL) |
| checkin_at | DateTime(tz) | 입실시각 (NOT NULL) |
| checkout_at | DateTime(tz) | 퇴실시각 (nullable) |
| duration_minutes | Integer | 체류시간 STORED Computed — checkout 후 db.refresh(record) 필수 |
| note | String(200) | 이석 사유 — PM외부대기·면담·지각·반차·조퇴·누락 등 (nullable) |
| created_at | DateTime(tz) | 생성 시각 |

**유니크 인덱스**: (worker_id) WHERE checkout_at IS NULL — 동시 이중 입실 방지
**GPS 미적용**: 위치 확인은 사용자가 현장·공정을 직접 선택하는 방식으로 대체

### schedules 테이블 (신규)
| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | BigInt PK | 자동증가 |
| worker_id | BigInt FK | workers.id |
| date | Date | 근무 날짜 (NOT NULL) |
| company | String(100) | 업체 (삼성전자 등) |
| site | String(100) | 위치 (P3 라인 A동 등) |
| process | String(100) | 공정 (포토 공정 등) |
| task | String(100) | 하는 일 (설비 점검 등) |
| created_at | DateTime(tz) | 생성 시각 |

**작업자 앱 활용**: 오늘 날짜 기준 스케줄 자동 조회 → "이 정보로 입실" → work_record 자동 생성
**정보 수정하기**: 스케줄 무시하고 업체→위치/공정→하는 일 처음부터 수동 선택

### worker_documents 테이블 (신규)
| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | BigInt PK | 자동증가 |
| worker_id | BigInt FK | workers.id |
| doc_type | String(50) | resident_copy / resume / application / pre_survey |
| file_path | String | 저장 경로 |
| uploaded_at | DateTime(tz) | 업로드 시각 |

### notices 테이블 (신규)
| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | BigInt PK | 자동증가 |
| title | String(200) | 공지 제목 (NOT NULL) |
| content | Text | 공지 내용 |
| created_by | String(100) | 작성자 (JWT sub) |
| created_at | DateTime(tz) | 생성 시각 |

### sites 테이블 (신규)
| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | BigInt PK | 자동증가 |
| name | String(100) | 사업장명 (NOT NULL) — 예: 삼성전자 온양사업장, SKHynix 청주사업장 |
| company | String(100) | 고객사 (삼성전자 / SK하이닉스 / 하나마이크론 등) |
| created_at | DateTime(tz) | 생성 시각 |

**관리자 웹에서 CRUD** — 사업장 추가·수정·삭제
**GPS 미적용**: 주소·GPS 좌표 없음. 사용자가 목록에서 직접 선택하는 방식으로 운영

### audit_logs 테이블
| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | BigInt PK | 자동증가 |
| actor | String(100) | 행위자 (JWT sub) |
| action | String(50) | 행위 유형 |
| target_id | BigInt | 대상 레코드 ID (nullable) |
| detail | Text | 상세 내용 (nullable) |
| created_at | DateTime(tz) | 발생 시각 |

---

## 환경 구조 원칙 (필수 숙지)

### 기본 원칙
지금까지 작성된 모든 Docker 및 인프라 구성은 Production 버전으로 간주한다.
앞으로는 기존 Production 구성도 모두 검토하여 대응되는 Development 버전을 함께 작성한다.
새로운 기능뿐 아니라 기존 코드도 Development 버전이 없다면 반드시 추가한다.

### 규칙
- 모든 Docker 관련 수정은 반드시 Production 버전과 Development 버전 두 가지를 모두 작성한다.
- 기존 Production 코드는 삭제하거나 변경하지 않는다.
- Development 구성은 별도 파일(Dockerfile.dev, docker-compose.dev.yml)로 관리한다.

### 파일 구분
| 파일 | 용도 |
|---|---|
| Dockerfile | 프로덕션 |
| Dockerfile.dev | 개발 |
| docker-compose.yml | 프로덕션 |
| docker-compose.dev.yml | 개발 |
| .env | 프로덕션 |
| .env.dev | 개발 |

---

## 작업 원칙
- 다음 작업 순서를 반드시 따른다.
- 이미 정해진 작업 순서를 임의로 변경하지 않는다.
- 사용자가 별도로 요청하지 않는 이상 다음 단계로 넘어가지 않는다.
- 현재 단계가 완료된 후에만 다음 단계를 진행한다.
- 파일을 생성·수정하기 전에 반드시 내용을 먼저 보여주고 확인을 받는다.

---

## 기존 코드 수정 원칙
- 기존 파일은 가능한 한 최소한으로 수정한다.
- 이미 구현된 기능은 유지한다.
- 필요한 부분만 변경한다.
- 파일 전체를 다시 작성하지 않는다.
- Breaking Change를 만들지 않는다.
- 기존 API, 프로젝트 구조, 설계 원칙을 유지한다.

---

## 답변 형식 (항상 이 순서로 답변)
1. 현재 Production 변경 사항
2. Development 대응 버전
3. 변경 이유
4. 장단점
5. 적용 방법

---

## 완성된 파일

### 프로덕션
- Dockerfile — 실제 서버 배포용 이미지 빌드 설정. 멀티스테이지로 용량 최적화됨
- docker-compose.yml — 프로덕션 컨테이너 묶음 실행 설정 (API + DB). 볼륨 바인드 없음
- .env — 실제 운영 환경변수 (DB 비밀번호, JWT 시크릿 등). **git에 절대 올리면 안 됨**
- .env.example — .env 템플릿. 민감 정보 없이 어떤 값이 필요한지만 표시. git 공유용
- .gitignore — git에 올리지 않을 파일 목록 (.env·.venv·로그·캐시 파일 등)
- .dockerignore — Docker 이미지에 포함하지 않을 파일 목록. 가상환경·캐시 등 제외해서 용량 줄임
- alembic/env.py — DB 마이그레이션 도구(Alembic)의 동작 방식 코드. .env와 이름 비슷하지만 전혀 다른 파일. 코드만 있어서 git에 올려도 됨
- alembic/versions/9614d542c65d_init.py — 2026-06-26 최초 DB 테이블 생성 마이그레이션 (audit_logs·workers·work_records 3개). wegov_dev DB에 적용 완료. ⚠️ role·hashed_birth·site·squad·round·GPS 컬럼은 이 파일엔 없음 → 0단계에서 추가 마이그레이션 필요
- app/models/worker.py — 근로자(workers) DB 테이블 구조 정의. 컬럼: id·name·company·phone·role·hashed_birth·site·squad·is_active·version·created_at
- app/models/work_record.py — 입실·퇴실 기록(work_records) DB 테이블 구조 정의. 컬럼: id·worker_id·round·process·checkin_at·checkout_at·duration_minutes·latitude·longitude·distance_meters·aux_auth·created_at
- app/models/audit_log.py — 관리자가 승인·반려·수정 등 어떤 행위를 했을 때 "누가·언제·무엇을 했다" 자동 기록 테이블
- app/models/__init__.py — 모델 모듈 묶음 초기화 파일. 직접 수정할 일 없음
- app/core/database.py — DB 연결 설정. 비동기 방식으로 PostgreSQL에 연결
- app/core/exceptions.py — 앱 시작/종료 처리, 공통 에러 핸들러 등록
- app/core/audit.py — 관리자 행위를 audit_log 테이블에 저장하는 공통 함수
- app/core/config.py — .env 파일을 읽어서 앱 전체 설정값으로 관리
- app/core/security.py — JWT 토큰(로그인 시 발급되는 임시 신분증) 생성·검증, 비밀번호 bcrypt 암호화 처리
- app/core/deps.py — 라우터에서 "현재 로그인한 사람이 누구인지" 확인하는 공통 함수. 관리자·작업자·리더 모두 이 함수를 거침. 역할 구분은 각 라우터에서 별도 처리
- app/main.py — FastAPI 앱 진입점. 현재 라우터 미등록 상태 (2단계에서 추가 예정)

### 개발
- Dockerfile.dev — 로컬 개발용 이미지. 코드 저장 시 서버 자동 재시작. 매번 빌드 불필요
- docker-compose.dev.yml — 개발 컨테이너 구성. 내 PC 폴더와 컨테이너를 직접 연결해서 코드 수정이 바로 반영됨
- .env.dev — 개발 환경변수. wegov_dev DB 사용, 주소는 로컬(localhost)

---

## 미완성 — 진행 체크리스트

완료 시 `- [ ]` → `- [x]` 로 변경

### 0단계: 모델·스키마 확정 (라우터 전 필수)
- [ ] workers 테이블 신규 컬럼 추가 — team·group_name·squad·line·work_status·status(8가지) 반영. GPS 컬럼(latitude·longitude·distance_meters·aux_auth) 제거
- [ ] work_records 테이블 수정 — GPS 컬럼 제거, site_name·shift_type·note 컬럼 추가
- [ ] schedules 테이블 신규 작성 — 작업자별 근무 스케줄 저장 (날짜·사업장·공정·근무표유형)
- [ ] worker_documents 테이블 신규 작성 — 근로자 서류 파일 경로 저장 (주민등록등본·이력서 등)
- [ ] notices 테이블 신규 작성 — 관리자가 작성하는 공지사항 저장
- [ ] sites 테이블 신규 작성 — 사업장 정보 저장 (GPS 없음. 이름·고객사만)
- [ ] 마이그레이션 적용 — 위 변경 내용을 실제 DB에 반영

### 1단계: 라우터 작성 (총 10개) — 현재 0개 완료
- [ ] app/routers/auth.py — 로그인(이름+생년월일), 계정 최초 활성화(주민번호 인증), JWT 토큰 발급
- [ ] app/routers/checkin.py — 입실 버튼 처리. 오늘 스케줄 있으면 자동, 없으면 수동 선택
- [ ] app/routers/checkout.py — 퇴실 버튼 처리. 체류시간 자동 계산
- [ ] app/routers/records.py — 출입 기록 조회 (일별·월별)
- [ ] app/routers/stats.py — 통계 집계. 고객사별·공정별·작업자별 + 엑셀 다운로드
- [ ] app/routers/correction.py — 입퇴실 수정 요청 등록, 관리자 승인·반려 처리
- [ ] app/routers/workers.py — 근로자 등록·수정·퇴사 처리 (관리자 전용)
- [ ] app/routers/schedules.py — 근무 스케줄 등록·조회
- [ ] app/routers/sites.py — 사업장 추가·수정·삭제 (관리자 전용)
- [ ] app/routers/notices.py — 공지사항 등록·수정·삭제

### 2단계
- [ ] app/main.py — 완성된 라우터 10개 전부 등록

### 파생 작업 (라우터 완성 이후)
- [ ] CORS 설정 — 프론트엔드 웹 주소에서 백엔드 호출 허용
- [ ] API 명세서 공유 — Railway 배포 후 /docs URL을 프론트 개발자에게 공유
- [ ] Railway 배포 — 앱 서버 + PostgreSQL 실서버 배포

---

## 1차 피드백 반영 사항
1. 코드 기반 계정 활성화 — 주민번호를 코드로 사용, 최초 1회 후 이름+생년월일 로그인
2. 관리자에서 사업장/근무지 추가 — sites 테이블 + CRUD API
3. 고객사별 통계 — stats 라우터에서 company 기준 집계
4. UI 컬러 — 미확정, UI 담당자 결정 후 반영

---

## 작업자 앱 입실 플로우 (C파트 참고용)

**GPS 미적용 — 사용자가 직접 선택하는 방식으로 변경 (2026-07-09 확정)**

```
앱 실행
↓
오늘 스케줄 있음?
├── YES → 스케줄 확인 화면 (사업장·공정·하는 일 자동 표시)
│         ├── "이 정보로 입실" → work_record 생성 (GPS 없음)
│         └── "정보 수정하기" → 사업장부터 수동 선택
└── NO  → 수동 선택 플로우
           ① 사업장 선택 (삼성전자 온양/천안, SKHynix 청주 등)
           ② 공정 선택 (사업장별 공정 목록에서 선택)
           ③ 근무표 유형 선택 (D/S/O/주/야)
           → work_record 생성 (GPS 없음)
```

**실제 공정명 (제조3팀 출입기록 기준):**
- 2라인 몰드 세정 / 4라인 몰드 세정
- 4라인 캐리어박스
- C동 릴머지
- C동 모듈 세정

**근무표 유형 5가지:** D(데이) / S(스윙) / O(오피스) / 주(주간) / 야(야간)

---

## Alembic 규칙

### 프로덕션
- revision 생성 금지. 생성된 migration 파일만 upgrade한다.
- 실행: `docker compose run --rm api alembic upgrade head`

### 개발
- revision은 반드시 개발 환경에서만 생성한다.
- docker-compose.dev.yml의 Bind Mount를 이용하여
  revision 파일이 로컬 alembic/versions에 자동 저장되어야 한다.
- 실행: `docker compose -f docker-compose.dev.yml run --rm api alembic revision --autogenerate -m "설명"`

---

## 핵심 설계 결정 (변경 금지)
- SQLAlchemy 2.0 async 스타일 (async with session)
- Worker 조회: `select(Worker).where(Worker.id == id, Worker.active_filter())`
- `await Worker.active()` 절대 금지 (Select 객체 반환)
- Worker 물리 삭제 금지 — is_active=False soft delete만
- duration_minutes (persisted=True, STORED) — PostgreSQL virtual 미지원. checkout 후 db.refresh(record) 권장
- save_audit_log: actor는 반드시 Depends(get_current_user) 주입, raw string 금지
- get_current_user 반환 타입: str (JWT sub 값 — 사용자 식별자)
- 모든 컬럼 nullable 명시 필수 (nullable=False 또는 nullable=True 생략 없이)
- .env / .env.dev git 커밋 금지
- 보안 최우선

### Worker role 설계
- role 값: "worker"(작업자) / "leader"(리더) / "admin"(지원팀·관리자)
- 라우터 접근 제어: worker=본인 기록만 / leader=팀 조회 / admin=전체 조회+수정승인
- server_default="worker" — 신규 등록 시 기본값

### GPS 미적용 (2026-07-09 의뢰처 요청으로 제외 확정)
- GPS 기능 전면 제외. 위치 확인은 사용자가 직접 현장·라인·공정을 선택하는 방식으로 대체
- work_records에 latitude·longitude·distance_meters·aux_auth 컬럼 없음
- sites 테이블에 GPS 관련 컬럼 없음

### correction 수정 유형 4가지
- CHECKIN_MISS: 입실 누락 — 실제 입실시간·공정·사유 입력 → 관리자 승인. 현장에서 PM외부대기·면담 등으로 발생
- CHECKOUT_MISS: 퇴실 누락 — 퇴실 수정 요청 → 관리자 승인
- WRONG_PRESS: 잘못 누름 — 작업자 직접 삭제 불가, 수정 요청으로만 처리
- LONG_STAY: 장시간 미퇴실 — 리더·관리자 알림 대상
- 예외처리 원칙: 원본 기록 보존, 관리자 승인, 수정 전·후 이력 및 사유 저장

### 이석(비고) 사유 유형 — 실제 출입기록 기반
- PM외부대기: 설비 점검 중 라인 밖 대기. 가장 빈번한 공백 원인
- 면담: 팀장·부장 면담으로 인한 공백
- 지각: 지각 기록
- 반차: 반차 처리
- 조퇴: 조기 퇴근
- 누락: 입실·퇴실 버튼 미처리
- 출입기록 누락: 방문 출입증 미처리로 시스템 기록 없음

### D파트 UI에서 확인된 correction 처리 흐름
- 승인(approved): realtimeData.status를 'normal'로 변경 + 이상알림 목록에서 제거
- 반려(rejected): 이상알림 유지 + "반려됨" 배지 표시 (재요청 유도)
- entry-miss-exit: 입실 누락 + 퇴실만 기록된 상태 — CHECKIN_MISS 유형에 해당
- dailyData.note: 수정 요청 사유 텍스트 — correction API에서 reason 필드로 저장 예정

### 자정 초과 처리 (슬라이드 6 기준)
- 자정을 넘어도 하나의 work_record로 연결 (날짜 기준 분리 없음)
- 집계 시 checkin_at 날짜 기준으로 그룹핑

### 엑셀 출력 요건 — 실제 출입기록 양식 기준 (출입기록 관리 파일_제조3팀 06.01~06.30.xlsx)
- stats 라우터에서 제공
- 출력 항목: 직원별 일일 상세기록 / 공정별 총 작업시간·투입인원·횟수·평균 / 작업자별 월간 총 라인 작업시간·누락·수정 건수
- 양식: 현재 지원팀 관리 양식과 최대한 동일하게 출력
- 회차별 입실·퇴실 시각 분리 (최대 6회차)
- 회차별 작업시간 분리 (1작업시간~6작업시간)
- 휴게시간 분리 (휴게시간1~휴게시간5)
- 총작업시간 / 총휴게시간 / 실제작업시간 / 실제휴식시간 / 근무시간 각각 출력
- 지각여부 / 휴게시간초과 / 비고(이석사유) 포함
- 근무표 유형 D/S/O/주/야 반영

---

## 현재 컨테이너 상태
- wegov-db-1 (dev): 실행 중 (healthy, 포트 5432, wegov_dev DB)
- api 이미지 (dev): 빌드 완료 (Dockerfile.dev 기준) — 라우터 추가 후 재빌드 필요
- api 이미지 (prod): 재빌드 필요 (Dockerfile 변경됨)
- alembic/versions/9614d542c65d_init.py: 완료, wegov_dev DB 적용 완료
- 모델 변경 완료 (마이그레이션 미적용 — 라우터 완성 후 진행):
  - workers.role 컬럼 (worker/leader/admin)
  - workers.company 컬럼 (협력업체 구분)
  - work_records.round 컬럼 (회차)
- ⚠️ GPS 기능 제외 확정 (2026-07-09) — work_records·sites 모델에서 GPS 컬럼 제거 필요 (0단계 작업)
- 다음 재개 시: app/routers/checkin.py 작성 시작

---

## 브랜치 전략
- 기능 단위 브랜치 → PR → main merge. main 직접 push 금지.
- 예: feature/router-checkin, feature/router-checkout, feature/router-records
- 라우터 5개 각각 별도 브랜치로 분리

## CLAUDE.md 관리
- 경로: C:\sat\wegov\CLAUDE.md (미작성 — 라우터 완성 후 작성 예정)
- 포함 항목: DB 스키마 요약, API 엔드포인트 목록, 변수명 규칙, 핵심 설계 결정
- 라우터 추가 / 모델 변경 시마다 동시 업데이트