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
5. **Admin** - 관리자 여정 승인/반려 및 포인트 지급
6. **EcoPass** - 에코패스 관리 (추가 기능)

### 프로젝트 현황

- ✅ 데이터베이스 스키마 완성 (Supabase migrations)
- ✅ 5개 도메인 엔티티 정의 (User, Station, ParkingLot, Trip, EcoPass)
- ✅ 6개 API 모듈 구현 (auth, admin, stations, trips, storage, ecopass)
- ✅ JWT 인증 시스템
- ✅ 테스트 코드 작성 (pytest)
- ✅ Postman Collection
- ✅ API 문서 자동 생성 (Swagger/ReDoc)
- ✅ 유틸리티 스크립트 (데이터 마이그레이션 도구)

## 🔥 코딩 규칙 (Coding Standards)

### 1. 스키마 명명 규칙 (Schema Naming Convention)

**MUST FOLLOW**: 모든 요청/응답 스키마는 아래 명명 규칙을 **반드시** 따라야 합니다.

- **요청 스키마**: `~~Request` (예: `CreateEcoPassRequest`, `UpdateEcoPassRequest`)
- **응답 스키마**: `~~Response` (예: `EcoPassResponse`, `EcoPassListResponse`)
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
if not ecopass:
    raise NotFoundError(f"EcoPass {id}를 찾을 수 없습니다")

# 나쁜 예: 불필요한 try-catch
try:
    ecopass = repository.get(id)  # 이미 예외 처리가 되어있는 경우
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
│   │   ├── trip.py          # 여정 엔티티 (3단계 상태 관리)
│   │   └── ecopass.py       # 에코패스 엔티티
│   └── repositories/         # 레포지토리 인터페이스
│
├── application/              # Application Layer (유스케이스)
│   └── services/            # 애플리케이션 서비스
│       ├── auth_service.py       # 인증 로직
│       ├── station_service.py    # 역 조회 로직
│       ├── trip_service.py       # 여정 관리 로직
│       ├── storage_service.py    # 파일 업로드 로직
│       ├── admin_service.py      # 관리자 로직
│       └── ecopass_service.py    # 에코패스 로직
│
├── infrastructure/           # Infrastructure Layer (외부 시스템)
│   ├── database/            # Supabase 클라이언트
│   └── repositories/        # 레포지토리 구현체
│
├── api/                      # API Layer (프레젠테이션)
│   ├── routes/              # FastAPI 라우터 (6개 모듈)
│   ├── schemas/             # Request/Response DTO
│   └── dependencies/        # 의존성 주입
│
├── shared/                   # Shared Kernel
│   ├── schemas/             # 공통 스키마 (SuccessResponse, ErrorResponse)
│   ├── utils/               # 유틸리티 함수
│   └── exceptions.py        # 커스텀 예외 클래스
│
├── config.py                # 환경 설정 (pydantic-settings)
└── main.py                  # FastAPI 앱 팩토리

tests/                        # 테스트 코드
├── test_auth.py             # 인증 API 테스트
├── test_stations.py         # 역 API 테스트
├── test_trips.py            # 여정 API 테스트
├── test_storage.py          # 스토리지 API 테스트
├── test_admin.py            # 관리자 API 테스트
└── test_integration.py      # 통합 테스트

scripts/                      # 유틸리티 스크립트
├── migrate_image_urls_to_signed.py  # public URL → Signed URL 마이그레이션
└── README.md                # 스크립트 사용 가이드

supabase/                     # Supabase 설정
├── migrations/              # 데이터베이스 마이그레이션
└── seed.sql                 # 샘플 데이터 (14개 역, 9개 주차장)
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
  "message": "EcoPass created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user_123",
    "title": "Green Commuter Pass",
    "points": 100
  }
}
```

### Error Response Example

```json
{
  "status": "error",
  "message": "EcoPass with id 550e8400-e29b-41d4-a716-446655440000 not found",
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
- RLS (Row Level Security) 정책 적용

**Authentication**: Supabase Auth

- JWT 토큰 기반 인증
- 회원가입/로그인 통합

**Storage**: Supabase Storage

- 인증 이미지 업로드 (`trips` 버킷)
- JWT 인증 기반 접근 제어

> **API 엔드포인트**: 전체 API 목록은 README.md 또는 http://localhost:8000/docs 참조

## Supabase MCP 워크플로우

이 프로젝트는 Supabase CLI 대신 **Supabase MCP**를 사용하여 데이터베이스를 관리합니다.

### 마이그레이션 적용

```python
# 1. 마이그레이션 파일 작성
vim supabase/migrations/20251227_add_rewards_table.sql

# 2. MCP로 적용
mcp__supabase__apply_migration(
    name="add_rewards_table",
    query=open("supabase/migrations/20251227_add_rewards_table.sql").read()
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

프로젝트에는 포괄적인 테스트 스위트가 구현되어 있습니다:

- **API 테스트**: FastAPI TestClient 사용 (6개 테스트 파일)
- **통합 테스트**: 실제 Supabase 인스턴스 연동 테스트
- **커버리지**: `pytest-cov`로 코드 커버리지 측정

**테스트 실행**:

```bash
uv run pytest                           # 전체 테스트
uv run pytest tests/test_auth.py        # 특정 모듈
uv run pytest --cov=src --cov-report=html  # 커버리지
```

## 체크리스트 (새 기능 추가 시)

- [ ] SQLModel 엔티티에 `table=True` 및 `__tablename__` 설정
- [ ] Request는 `~Request`, Response는 `~Response` 명명 규칙
- [ ] BaseRequest, BaseResponse 상속
- [ ] 한글 주석 1-2줄 필수
- [ ] BaseAppException 계열 예외 사용
- [ ] `SuccessResponse.create()` 표준 응답 형식
- [ ] YAGNI 원칙 준수 (미래를 위한 코드 작성 금지)
