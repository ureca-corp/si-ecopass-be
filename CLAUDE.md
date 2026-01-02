# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SI-EcoPass Backend** - 대구 지하철 환승 주차장 이용 장려 플랫폼의 백엔드 API

- **Language**: Python 3.12+
- **Framework**: FastAPI with Uvicorn
- **Package Manager**: `uv` (fast Python package installer and resolver)
- **Database**: Supabase (PostgreSQL + PostGIS)
- **ORM**: SQLModel (Pydantic + SQLAlchemy integration)
- **Architecture**: Domain-Driven Design (DDD)
- **API Standard**: All responses follow `{status, message, data}` format

### 구현된 주요 도메인

1. **Authentication** - 사용자 회원가입, 로그인, 프로필 관리 (Supabase Auth 통합)
2. **Stations** - 대구 지하철 1/2/3호선 역 및 주변 주차장 조회 (PostGIS 기반)
3. **Trips** - 여정 3단계 관리 (출발 → 환승 → 도착)
4. **Storage** - Supabase Storage를 통한 인증 이미지 업로드
5. **Admin** - 관리자 여정 승인/반려 및 포인트 지급, 역/주차장 관리

### 프로젝트 현황

- ✅ 데이터베이스 스키마 완성 (Supabase migrations)
- ✅ 4개 도메인 엔티티 정의 (User, Station, ParkingLot, Trip)
- ✅ 6개 API 모듈 구현 (auth, admin, stations, parking-lots, trips, storage)
- ✅ JWT 인증 시스템
- ✅ 테스트 코드 작성 (pytest)
- ✅ Postman Collection
- ✅ API 문서 자동 생성 (Swagger/ReDoc)
- ✅ 유틸리티 스크립트 (데이터 마이그레이션 도구)

## 🔥 코딩 규칙 (Coding Standards)

### 1. 스키마 명명 규칙 (Schema Naming Convention)

**MUST FOLLOW**: 모든 요청/응답 스키마는 아래 명명 규칙을 **반드시** 따라야 합니다.

- **요청 스키마**: `~~Request` (예: `CreateTripRequest`, `UpdateStationRequest`)
- **응답 스키마**: `~~Response` (예: `TripResponse`, `StationListResponse`)
- **베이스 클래스**: 모든 Request는 `BaseRequest`, 모든 Response는 `BaseResponse` 상속

```python
from src.shared.schemas.base import BaseRequest, BaseResponse

class CreateSomethingRequest(BaseRequest):
    """요청 스키마"""
    field: str

class SomethingResponse(BaseResponse):
    """응답 스키마"""
    id: UUID
    field: str
```

### 2. 예외 처리 (Exception Handling)

- **모든 예외는 `BaseAppException`을 상속**하여 일관성 유지
- 예외는 자동으로 `JSONResponse`로 변환되어 표준 응답 형식으로 반환됨
- **불필요한 try-catch 남용 금지** - 예외는 명확한 이유가 있을 때만 처리

```python
from src.shared.exceptions import NotFoundError, ValidationError

# 좋은 예: 명확한 비즈니스 로직 검증
if not trip:
    raise NotFoundError(f"Trip {id}를 찾을 수 없습니다")

# 나쁜 예: 불필요한 try-catch
try:
    trip = repository.get(id)  # 이미 예외 처리가 되어있는 경우
except Exception as e:
    raise InternalServerError(str(e))  # 불필요한 래핑
```

### 3. 한글 주석 (Korean Comments)

- **모든 함수와 클래스에 한글 주석 1-2줄 필수**
- 코드 자체가 명확한 경우 간결하게, 복잡한 로직은 상세하게
- 리팩토링을 고려하여 "왜"에 집중

```python
def calculate_points(activities: list[Activity]) -> int:
    """
    활동 목록에서 총 포인트를 계산
    중복 활동은 제외하고 유효한 활동만 합산
    """
    pass
```

### 4. 불필요한 코드 작성 금지

- **미래를 위한 코드 작성 금지** - YAGNI (You Aren't Gonna Need It) 원칙
- 현재 사용하지 않는 함수, 클래스, 상수는 작성하지 않음
- 필요할 때 추가하는 것이 리팩토링하기 더 쉬움

## Quick Start

### 기본 명령어

```bash
# 의존성 설치
uv sync

# 서버 실행 (개발 모드, 핫 리로드)
uv run python main.py

# 테스트 실행
uv run pytest

# 테스트 커버리지
uv run pytest --cov=src --cov-report=html
```

### API 문서

서버 실행 후 다음 URL에서 확인:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Project Structure (Domain-Driven Design)

```
src/
├── domain/                    # Domain Layer (비즈니스 로직 핵심)
│   ├── entities/             # 도메인 엔티티 (SQLModel)
│   │   ├── user.py          # 사용자 엔티티
│   │   ├── station.py       # 역 엔티티 (PostGIS)
│   │   ├── parking_lot.py   # 주차장 엔티티
│   │   └── trip.py          # 여정 엔티티 (3단계 상태 관리)
│   └── repositories/         # 레포지토리 인터페이스
│
├── application/              # Application Layer (유스케이스)
│   └── services/            # 애플리케이션 서비스
│       ├── auth_service.py       # 인증 로직
│       ├── station_service.py    # 역/주차장 조회 로직
│       ├── trip_service.py       # 여정 관리 로직
│       ├── storage_service.py    # 파일 업로드 로직
│       └── admin_service.py      # 관리자 로직
│
├── infrastructure/           # Infrastructure Layer (외부 시스템)
│   ├── database/            # Supabase 클라이언트 및 SQLModel 세션
│   └── repositories/        # 레포지토리 구현체
│
├── api/                      # API Layer (프레젠테이션)
│   ├── routes/              # FastAPI 라우터 (6개 모듈)
│   │   ├── auth_routes.py        # 인증 API
│   │   ├── station_routes.py     # 역 조회 API
│   │   ├── parking_lot_routes.py # 주차장 조회 API
│   │   ├── trip_routes.py        # 여정 관리 API
│   │   ├── storage_routes.py     # 이미지 업로드 API
│   │   └── admin_routes.py       # 관리자 API
│   ├── schemas/             # Request/Response DTO
│   └── dependencies/        # 의존성 주입
│
├── shared/                   # Shared Kernel
│   ├── schemas/             # 공통 스키마 (SuccessResponse, ErrorResponse)
│   ├── utils/               # 유틸리티 함수 (file_validation 등)
│   └── exceptions.py        # 커스텀 예외 클래스
│
├── config.py                # 환경 설정 (pydantic-settings)
└── main.py                  # FastAPI 앱 팩토리

tests/                        # 테스트 코드 (도메인별 분리)
├── conftest.py              # pytest 공통 설정 및 fixture
├── auth/
│   └── test_auth.py         # 인증 API 테스트
├── stations/
│   ├── test_station_queries.py      # 역 조회 API 테스트
│   └── test_admin_station_crud.py   # 관리자 역 CRUD 테스트
├── parking_lots/
│   ├── test_parking_lot_queries.py      # 주차장 조회 API 테스트
│   └── test_admin_parking_lot_crud.py   # 관리자 주차장 CRUD 테스트
├── trips/
│   ├── test_trip_lifecycle.py      # 여정 생명주기 테스트 (시작/환승/도착)
│   ├── test_trip_queries.py        # 여정 조회 테스트
│   └── test_admin_trip_approval.py # 관리자 여정 승인/반려 테스트
├── storage/
│   └── test_storage.py      # 스토리지 API 테스트
└── integration/
    └── test_integration.py  # 통합 테스트

scripts/                      # 유틸리티 스크립트
├── create_admin_user.py           # 관리자 계정 생성
├── import_station_data.py         # 역/주차장 데이터 임포트
├── migrate_image_urls_to_signed.py  # public URL → Signed URL 마이그레이션
├── cleanup_local_db.py            # 로컬 Supabase 테스트 데이터 정리
└── cleanup_test_data.sql          # SQL 직접 실행용 정리 스크립트

supabase/                     # Supabase 설정
├── migrations/              # 데이터베이스 마이그레이션
│   ├── README.md           # 마이그레이션 목록 및 설명
│   └── *.sql               # 활성 마이그레이션 (9개, 정리됨)
├── seed.sql                 # Seed 데이터 (14개 역, 9개 주차장)
└── config.toml              # 로컬 Supabase 설정
```

## Architecture Principles

### Domain-Driven Design (DDD)

1. **Domain Layer**: Pure business logic, no external dependencies

   - Entities contain business rules and domain logic
   - Repositories define interfaces (contracts) for data access
   - No knowledge of FastAPI, Supabase, or HTTP

2. **Application Layer**: Orchestrates domain objects

   - Services coordinate between domain and infrastructure
   - Implements use cases and business workflows
   - No direct knowledge of HTTP or database implementations

3. **Infrastructure Layer**: External concerns

   - Repository implementations (Supabase, in-memory, etc.)
   - External API clients
   - Database connections and queries

4. **API Layer**: HTTP/REST interface
   - FastAPI routes and endpoints
   - Request/Response schemas (DTOs)
   - Dependency injection for services

### Dependency Rule

Dependencies flow inward: `API → Application → Domain`

- Domain has no dependencies on outer layers
- Application depends only on Domain
- Infrastructure implements Domain interfaces
- API depends on Application and uses Infrastructure via DI

## Standardized API Response Format

All API endpoints return responses in this format:

```json
{
  "status": "success" | "error",
  "message": "Human-readable message",
  "data": { ... } | null
}
```

### Success Response Example

```json
{
  "status": "success",
  "message": "Trip created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user_123",
    "status": "departing",
    "points": 100
  }
}
```

### Error Response Example

```json
{
  "status": "error",
  "message": "Trip with id 550e8400-e29b-41d4-a716-446655440000 not found",
  "data": null
}
```

## Key Dependencies

- **fastapi** - Modern web framework with automatic OpenAPI documentation
- **uvicorn** - ASGI server for running FastAPI
- **pydantic** - Data validation and settings management
- **pydantic-settings** - Environment variable management
- **python-dotenv** - Load environment variables from .env
- **supabase** - Python client for Supabase (PostgreSQL backend, auth, storage, realtime)
- **sqlmodel** - SQLAlchemy + Pydantic integration for type-safe DB models

## 주요 기술 스택 & 통합

### SQLModel 엔티티

모든 도메인 엔티티는 `SQLModel`을 사용하여 정의:

- `table=True` 설정으로 DB 테이블 매핑
- `__tablename__` 명시 (Supabase 테이블명)
- Pydantic 검증 + SQLAlchemy 통합
- timezone-aware datetime 필드 사용

### Supabase 통합

**Database**: PostgreSQL 15+ with PostGIS

- UUID v7 사용 (시간 기반 정렬 가능)
- PostGIS로 지리적 좌표 및 거리 계산
- **RLS (Row Level Security) 비활성화** - JWT 인증으로 충분

**Authentication**: Supabase Auth

- JWT 토큰 기반 인증
- 회원가입/로그인 통합

**Storage**: Supabase Storage

- 인증 이미지 업로드 (`trips` 버킷)
- Signed URL 방식 (24시간 유효)
- 최소한의 RLS 정책만 유지 (버킷 메타데이터 조회)

> **API 엔드포인트**: 전체 API 목록은 README.md 또는 http://localhost:8000/docs 참조

## 🔒 보안 아키텍처

### JWT 기반 단일 인증 계층

이 프로젝트는 **RLS를 사용하지 않고 JWT 인증만 사용**하여 보안을 관리합니다.

**설계 결정 이유:**
1. ✅ **단순성**: 모든 보안 로직이 FastAPI 애플리케이션 계층에 집중
2. ✅ **디버깅 용이성**: 400/403 오류 발생 시 JWT만 확인하면 됨
3. ✅ **성능**: RLS 정책 평가 오버헤드 제거
4. ✅ **명확성**: 애플리케이션 코드에서 모든 권한 검증 확인 가능

**보안 계층:**

```
┌─────────────────────────────────────────────────┐
│  1. FastAPI Middleware                          │
│     - CORS 설정                                 │
│     - 요청/응답 로깅                            │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  2. JWT 인증 (auth_deps.py)                     │
│     - get_current_user() 의존성                │
│     - Supabase Auth로 토큰 검증                │
│     - 모든 보호된 엔드포인트에 적용             │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  3. Service Layer (소유권/권한 검증)           │
│     - StorageService: trip 소유권 검증         │
│     - TripService: 본인 여정만 수정 허용        │
│     - AdminService: admin 역할 확인            │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  4. Database (PostgreSQL)                       │
│     - RLS 비활성화 (public 테이블)             │
│     - Storage만 최소 RLS 유지                   │
└─────────────────────────────────────────────────┘
```

**인증 흐름:**

```python
# 1. 클라이언트 → API 요청
GET /api/v1/trips/my-trips
Authorization: Bearer <jwt_token>

# 2. FastAPI auth_deps.py에서 검증
async def get_current_user(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    user_response = db.auth.get_user(token)  # ← Supabase Auth 검증
    # users 테이블에서 조회 (필수)
    user = await auth_service.get_user_by_id(user_id)
    return user

# 3. Service에서 비즈니스 로직 검증
async def get_my_trips(user_id: UUID):
    # 이미 get_current_user를 통과했으므로 user_id는 신뢰 가능
    trips = await db.trips.filter(user_id=user_id).all()
    return trips
```

**관리자 인증 (별도 처리):**

```python
# admin_deps.py - 관리자는 users 테이블 없어도 동작
async def get_admin_user(credentials: HTTPAuthorizationCredentials):
    user_response = db.auth.get_user(token)
    user_metadata = user_response.user.user_metadata or {}
    role = user_metadata.get("role", "user")

    if role != "admin":
        raise ForbiddenError("관리자 권한이 필요합니다")

    # users 테이블 조회 시도 (선택)
    try:
        user = await auth_service.get_user_by_id(user_id)
    except Exception:
        # users 테이블에 없으면 user_metadata로 User 객체 생성
        user = User(id=user_id, email=email, role="admin", ...)

    return user
```

**signup() 보안 강화:**

```python
# auth_service.py - role 파라미터 제거 (보안)
async def signup(email: str, password: str, username: str):
    """
    일반 사용자만 회원가입 가능 (role은 항상 "user")
    관리자는 Supabase Dashboard나 스크립트로만 생성
    """
    auth_response = db.auth.sign_up({
        "email": email,
        "password": password,
        "options": {
            "data": {
                "username": username,
                "role": "user",  # 하드코딩 - 일반 사용자만
            }
        }
    })
```

**RLS 상태:**

| 테이블 | RLS 활성화 | 정책 수 | 비고 |
|--------|------------|---------|------|
| `users` | ❌ | 0 | JWT로 충분 |
| `trips` | ❌ | 0 | Service에서 소유권 검증 |
| `stations` | ❌ | 0 | 공개 데이터 |
| `parking_lots` | ❌ | 0 | 공개 데이터 |
| `storage.buckets` | ✅ | 1 | 버킷 메타데이터 조회 허용 |
| `storage.objects` | ✅ | 1 | trips 버킷 전체 접근 허용 |

**마이그레이션 이력:**
- `20251229000010_disable_all_rls.sql` - 모든 public 테이블 RLS 제거
- `supabase/migrations/README.md` - 전체 마이그레이션 목록 및 설명 (9개 활성 마이그레이션)
- **정리 완료**: 불필요한 함수 및 deprecated RLS 마이그레이션 제거됨

## Supabase 워크플로우

이 프로젝트는 **Supabase MCP**(프로덕션) 또는 **로컬 Supabase + psql**(테스트)을 사용합니다.

### 로컬 환경: psql 직접 사용 (권장)

```bash
# 1. psql 별칭 설정
alias psql-local='psql "postgresql://postgres:postgres@127.0.0.1:54322/postgres"'

# 2. 마이그레이션 파일 작성
vim supabase/migrations/20260101000001_add_rewards_table.sql

# 3. 로컬에서 마이그레이션 테스트
psql-local -f supabase/migrations/20260101000001_add_rewards_table.sql

# 4. 테스트 후 seed 데이터 재삽입
psql-local -f supabase/seed.sql

# 5. 데이터 확인
psql-local -c "\dt"  # 테이블 목록
psql-local -c "SELECT COUNT(*) FROM stations;"
```

### 프로덕션 환경: Supabase MCP

```python
# 1. 마이그레이션 파일 작성 (로컬에서 이미 테스트 완료)
vim supabase/migrations/20260101000001_add_rewards_table.sql

# 2. MCP로 프로덕션 적용
mcp__supabase__apply_migration(
    name="add_rewards_table",
    query=open("supabase/migrations/20260101000001_add_rewards_table.sql").read()
)
```

### 브랜치 기반 개발 (권장)

```python
# 1. 개발용 브랜치 생성 (프로덕션과 격리된 환경)
mcp__supabase__create_branch(
    name="feature-new-api",
    confirm_cost_id="..."  # 비용 확인 필요
)

# 2. 브랜치에서 마이그레이션 테스트
mcp__supabase__apply_migration(...)  # 브랜치 DB에 적용

# 3. 테스트 완료 후 프로덕션에 병합
mcp__supabase__merge_branch(branch_id="...")

# 4. 브랜치 삭제
mcp__supabase__delete_branch(branch_id="...")
```

### SQL 직접 실행

```python
# seed 데이터 삽입
mcp__supabase__execute_sql(
    query=open("supabase/seed.sql").read()
)

# 임시 쿼리 실행
mcp__supabase__execute_sql(
    query="SELECT * FROM stations WHERE line_number = 1"
)
```

### 데이터베이스 정보 조회

```python
# 테이블 목록
mcp__supabase__list_tables()

# 마이그레이션 이력
mcp__supabase__list_migrations()

# 보안/성능 분석
mcp__supabase__get_advisors(type="security")
```

## 개발 워크플로우

### 시나리오 1: 새 API 기능 추가

```bash
# 1. 도메인 엔티티 정의
vim src/domain/entities/reward.py

# 2. 마이그레이션 파일 작성
vim supabase/migrations/20251227_add_rewards.sql

# 3. MCP로 브랜치 생성 및 마이그레이션 적용 (프로덕션 안전)
# mcp__supabase__create_branch() → mcp__supabase__apply_migration()

# 4. 레포지토리 인터페이스 정의
vim src/domain/repositories/reward_repository.py

# 5. 레포지토리 구현
vim src/infrastructure/repositories/reward_repository_impl.py

# 6. 애플리케이션 서비스 작성
vim src/application/services/reward_service.py

# 7. API 스키마 정의 (Request/Response 명명 규칙)
vim src/api/schemas/reward_schemas.py

# 8. API 라우터 구현
vim src/api/routes/reward_routes.py

# 9. main.py에 라우터 등록

# 10. 테스트 작성
vim tests/test_rewards.py

# 11. 테스트 실행
uv run pytest tests/test_rewards.py

# 12. 성공하면 브랜치 병합 (mcp__supabase__merge_branch)
```

### 시나리오 2: 마이그레이션 안전 테스트

```python
# 1. 브랜치에서 새 마이그레이션 테스트
mcp__supabase__create_branch(name="test-migration")
mcp__supabase__apply_migration(...)

# 2. 문제 발생 시 브랜치 삭제 (프로덕션 영향 없음)
mcp__supabase__delete_branch(branch_id="...")

# 3. 마이그레이션 수정 후 재시도
```

### 시나리오 3: 프로덕션 배포

```bash
# 1. 모든 변경사항 커밋
git add .
git commit -m "Add rewards API"

# 2. 테스트 통과 확인
uv run pytest

# 3. 프로덕션 마이그레이션 적용 (브랜치에서 이미 검증됨)
# mcp__supabase__apply_migration() 또는 merge_branch()

# 4. 서버 배포
git push origin main
```

## 새로운 기능 추가 가이드 (DDD)

1. **Domain Entity** 정의 (`src/domain/entities/`)
2. **Application Service** 작성 (`src/application/services/`)
3. **API Schemas** 정의 (`src/api/schemas/`) - Request/Response 명명 규칙 준수
4. **API Routes** 구현 (`src/api/routes/`)
5. **Router 등록** (`src/main.py`)
6. **테스트 작성** (`tests/`)

### Custom Exceptions

모든 예외는 `BaseAppException`을 상속하며 자동으로 표준 에러 응답으로 변환:

- `NotFoundError` (404) - 리소스를 찾을 수 없음
- `ValidationError` (422) - 유효성 검증 실패
- `UnauthorizedError` (401) - 인증 필요
- `ForbiddenError` (403) - 권한 없음
- `ConflictError` (409) - 리소스 충돌
- `InternalServerError` (500) - 서버 내부 오류

### Environment Configuration

`.env` 파일에서 환경 변수 관리:

- `DEBUG` - 디버그 모드 활성화
- `SUPABASE_URL`, `SUPABASE_KEY` - Supabase 연결 정보
- `API_PREFIX=/api/v1` - API 경로 접두사
- `ALLOWED_ORIGINS` - CORS 설정

## 테스트 전략

프로젝트는 **로컬 Supabase Docker 환경**을 사용하여 테스트합니다:

- **API 테스트**: FastAPI TestClient 사용 (6개 테스트 파일)
- **통합 테스트**: 로컬 Supabase 인스턴스 연동 (프로덕션과 격리)
- **커버리지**: `pytest-cov`로 코드 커버리지 측정
- **장점**: Rate limit 없음, 빠른 실행 속도, 프로덕션 DB 오염 방지

### 로컬 Supabase 테스트 환경

#### 1. 로컬 Supabase 시작/종료

```bash
# Supabase Docker 시작 (최초 1회 실행)
supabase start

# 상태 확인
supabase status

# 종료
supabase stop

# 데이터베이스 리셋 (초기 상태로)
supabase db reset
```

**접속 정보** (supabase start 실행 후 표시):
- **Project URL**: http://127.0.0.1:54321
- **DB URL**: postgresql://postgres:postgres@127.0.0.1:54322/postgres
- **Studio**: http://127.0.0.1:54323 (웹 UI)
- **Publishable Key**: sb_publishable_... (출력 확인)

#### 2. 환경 변수 설정 (.env.test)

테스트 실행 시 `.env.test` 파일이 자동으로 로드됩니다:

```bash
# .env.test (로컬 Supabase 연결 정보)
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_KEY=sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres
```

#### 3. psql로 직접 데이터 관리

```bash
# psql 별칭 추가 (권장)
echo 'alias psql-local="psql \"postgresql://postgres:postgres@127.0.0.1:54322/postgres\""' >> ~/.zshrc
source ~/.zshrc

# 테이블 목록 확인
psql-local -c "\dt"

# 테스트 데이터 정리 (역/주차장 유지)
psql-local -c "DELETE FROM trips; DELETE FROM users;"

# Seed 데이터 삽입
psql-local -f supabase/seed.sql

# 데이터 개수 확인
psql-local -c "
  SELECT 'users' as table_name, COUNT(*) FROM users
  UNION ALL SELECT 'trips', COUNT(*) FROM trips
  UNION ALL SELECT 'stations', COUNT(*) FROM stations
  UNION ALL SELECT 'parking_lots', COUNT(*) FROM parking_lots;
"
```

#### 4. 테스트 실행

```bash
# 전체 테스트 (로컬 Supabase 자동 연결)
uv run pytest

# 도메인별 테스트 (권장: 명확한 범위 지정)
uv run pytest tests/auth/ -v          # 인증 API만
uv run pytest tests/trips/ -v         # 여정 API만
uv run pytest tests/stations/ -v      # 역 API만
uv run pytest tests/storage/ -v       # 스토리지 API만

# 특정 테스트 파일만
uv run pytest tests/trips/test_trip_lifecycle.py -v

# Coverage 무시
uv run pytest --no-cov

# 빠른 실행 (도메인별 병렬 처리)
uv run pytest -n auto
```

**테스트 격리**:
- ✅ 프로덕션 DB와 완전 분리
- ✅ Rate limit 없음 (로컬이므로 무제한)
- ✅ 빠른 실행 (네트워크 레이턴시 제거)
- ✅ 테스트 후 즉시 데이터 리셋 가능

#### 5. 도메인별 테스트 구조 (2026-01-02 개선)

**구조화 이점:**
- **명확한 범위**: 각 도메인이 독립적인 디렉토리를 가져 테스트 범위 명확화
- **병렬 실행 최적화**: `pytest -n auto`로 도메인별 병렬 처리 자동화
- **파일 크기 감소**: 715줄 test_admin.py → 3개 파일(각 100-300줄)로 분리
- **에이전트 효율성**: 각 에이전트가 독립적인 도메인 테스트에 집중 가능

**테스트 파일 분류:**
```
tests/
├── auth/              # 인증 (8 tests)
├── stations/          # 역 조회 + CRUD (7 tests)
├── parking_lots/      # 주차장 조회 + CRUD (7 tests)
├── trips/             # 여정 생명주기 + 조회 + 승인 (32 tests)
├── storage/           # 스토리지 (10 tests)
└── integration/       # 통합 시나리오 (4 tests)
```

**권장 실행 방법:**
```bash
# 도메인별 독립 실행 (디버깅 시)
uv run pytest tests/trips/ -v

# 전체 병렬 실행 (CI/CD)
uv run pytest -n auto

# 특정 기능만 (예: 여정 생명주기)
uv run pytest tests/trips/test_trip_lifecycle.py -v
```

## 체크리스트 (새 기능 추가 시)

- [ ] SQLModel 엔티티에 `table=True` 및 `__tablename__` 설정
- [ ] Request는 `~Request`, Response는 `~Response` 명명 규칙
- [ ] BaseRequest, BaseResponse 상속
- [ ] 한글 주석 1-2줄 필수
- [ ] BaseAppException 계열 예외 사용
- [ ] `SuccessResponse.create()` 표준 응답 형식
- [ ] YAGNI 원칙 준수 (미래를 위한 코드 작성 금지)

## 🐛 트러블슈팅 (Troubleshooting)

### Supabase Storage 400 오류

**증상:**
```
HTTP 400: {"statusCode":"400","error":"InvalidJWT","message":"\"exp\" claim timestamp check failed"}
```

**원인:**
- Signed URL의 JWT 토큰이 만료됨 (기본 24시간 유효)
- 클라이언트가 오래된 URL을 캐싱하여 재사용 중

**해결 방법:**

1. **서버에서 최신 URL 생성:**
```python
# storage_service.py
signed_url_response = self.storage.create_signed_url(
    file_path,
    expires_in=86400  # 24시간
)
return signed_url_response["signedURL"]
```

2. **Flutter 앱에서 매번 새 URL 요청:**
```dart
// ❌ 기존: DB에 저장된 URL 직접 사용
final imageUrl = trip.transferImageUrl;

// ✅ 개선: 서버에서 최신 URL 가져오기
final imageUrl = await api.getSignedImageUrl(tripId, stage: 'transfer');
```

3. **테스트:**
```bash
# 새로운 signed URL 생성 및 테스트
uv run python scripts/test_signed_url.py
```

**디버깅 체크리스트:**
- [ ] JWT 토큰 만료 확인 (`exp` claim)
- [ ] 파일이 실제로 Storage에 존재하는지 확인
- [ ] RLS 정책 확인 (현재는 최소화되어 있음)
- [ ] 버킷 이름 오타 확인 (`trips`)

**참고:**
- RLS를 제거했으므로 400 오류는 대부분 JWT 만료 또는 파일 없음
- Storage는 최소 RLS만 유지 (버킷 메타데이터 조회 허용)

### Database Connection 오류

**증상:**
```
pydantic_core._pydantic_core.ValidationError: Field required
```

**원인:**
- `.env` 파일의 필수 환경 변수 누락
- 환경 변수 이름 오타

**해결:**
```bash
# .env 파일 확인
cat .env | grep SUPABASE

# 필수 변수
SUPABASE_URL=...
SUPABASE_KEY=...
DATABASE_URL=...
```

### 마이그레이션 실패

**증상:**
```
ERROR: syntax error at or near "..."
```

**해결:**
1. SQL 문법 확인
2. 테이블/컬럼명 오타 확인
3. 브랜치에서 먼저 테스트:
```python
mcp__supabase__create_branch(name="test-migration")
mcp__supabase__apply_migration(...)
# 실패 시 브랜치 삭제
mcp__supabase__delete_branch(...)
```
