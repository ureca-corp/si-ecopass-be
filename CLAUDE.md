# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SI-EcoPass Backend** - A FastAPI backend service following Domain-Driven Design (DDD) principles with Supabase for data persistence.

- **Language**: Python 3.12+
- **Framework**: FastAPI with Uvicorn
- **Package Manager**: `uv` (fast Python package installer and resolver)
- **Database**: Supabase (PostgreSQL-based backend-as-a-service)
- **ORM**: SQLModel (Pydantic + SQLAlchemy integration)
- **Architecture**: Domain-Driven Design (DDD)
- **API Standard**: All responses follow `{status, message, data}` format

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

## Development Commands

### Package Management with uv

```bash
# Install dependencies
uv sync

# Add a new dependency
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>

# Update dependencies
uv lock --upgrade
```

### Running the Application

```bash
# Run the FastAPI application (with hot reload in debug mode)
uv run python main.py

# Alternative: Run with uvicorn directly
uv run uvicorn src.main:app --reload

# Production mode (no reload)
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### API Documentation

When the application is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

## Project Structure (Domain-Driven Design)

```
src/
├── domain/                    # Domain Layer (Business Logic Core)
│   ├── entities/             # Domain entities with business rules
│   ├── value_objects/        # Immutable value objects
│   └── repositories/         # Repository interfaces (contracts)
│
├── application/              # Application Layer (Use Cases)
│   ├── services/            # Application services (orchestration)
│   └── use_cases/           # Specific use case implementations
│
├── infrastructure/           # Infrastructure Layer (External Concerns)
│   ├── database/            # Database implementations
│   ├── external/            # External service integrations
│   └── repositories/        # Repository implementations
│
├── api/                      # Presentation Layer (HTTP/REST)
│   ├── routes/              # FastAPI routers (endpoints)
│   ├── schemas/             # Request/Response DTOs
│   └── dependencies/        # FastAPI dependency injection
│
├── shared/                   # Shared Kernel
│   ├── schemas/             # Common schemas (response models)
│   ├── utils/               # Utility functions
│   └── exceptions.py        # Custom exception classes
│
├── config.py                # Application configuration
└── main.py                  # FastAPI application factory

main.py                       # Application entry point
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

## SQLModel & Supabase Integration

### SQLModel 엔티티 정의

모든 도메인 엔티티는 `SQLModel`을 상속하여 정의합니다:

```python
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime

class MyEntity(SQLModel, table=True):
    """엔티티 설명"""
    __tablename__ = "my_entities"  # Supabase 테이블명

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(min_length=1, max_length=200)
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True))
    )
```

**핵심 포인트**:
- `table=True`: 실제 DB 테이블 매핑
- `__tablename__`: Supabase 테이블명 명시
- `Field()`: Pydantic 검증 + SQLAlchemy 매핑 통합
- `sa_column`: SQLAlchemy 고급 설정 (timezone-aware datetime 등)

### Supabase 클라이언트 사용

Supabase 클라이언트는 `src/infrastructure/database/supabase.py`에서 관리:

```python
from src.infrastructure.database.supabase import get_db

# FastAPI 의존성 주입
def some_repository(db: Client = Depends(get_db)):
    # Supabase 클라이언트 사용
    result = db.table("ecopasses").select("*").execute()
    return result.data
```

**주요 메서드**:
- `.table(name).select("*")` - 조회
- `.table(name).insert(data)` - 삽입
- `.table(name).update(data).eq("id", id)` - 수정
- `.table(name).delete().eq("id", id)` - 삭제

## Development Patterns

### Adding a New Feature (DDD Approach)

1. **Define the Domain Entity** in `src/domain/entities/`
   - SQLModel 기반으로 작성 (`table=True`)
   - 비즈니스 로직 메서드 추가 (예: `add_points()`, `activate()`)
   - 외부 의존성 없이 순수한 도메인 로직만 포함

2. **Create Repository Interface** in `src/domain/repositories/`
   - 데이터 접근 계약(인터페이스) 정의
   - 구현 세부사항은 포함하지 않음

3. **Implement Repository** in `src/infrastructure/repositories/`
   - Supabase 클라이언트를 사용한 구현
   - 도메인 인터페이스를 구현
   - SQLModel 엔티티와 Supabase 데이터 변환

4. **Create Application Service** in `src/application/services/`
   - 도메인 객체들을 조율
   - 유스케이스 구현 (예: `create_ecopass()`, `add_points()`)

5. **Define API Schemas** in `src/api/schemas/`
   - **Request 스키마**: `~~Request` (BaseRequest 상속)
   - **Response 스키마**: `~~Response` (BaseResponse 상속)
   - 한글 주석 필수

6. **Create API Routes** in `src/api/routes/`
   - FastAPI 엔드포인트 작성
   - 의존성 주입으로 서비스 사용
   - 표준 응답 형식 반환 (`SuccessResponse.create()`)

7. **Register Router** in `src/main.py`
   - API 접두사와 함께 라우터 등록

### Custom Exceptions

`src/shared/exceptions.py`에서 제공하는 커스텀 예외를 사용:

- `NotFoundError` - 리소스를 찾을 수 없음 (404)
- `ValidationError` - 유효성 검증 실패 (422)
- `UnauthorizedError` - 인증 필요 (401)
- `ForbiddenError` - 권한 없음 (403)
- `ConflictError` - 리소스 충돌 (409)
- `InternalServerError` - 서버 내부 오류 (500)

**사용 예시**:
```python
from src.shared.exceptions import NotFoundError

if not ecopass:
    raise NotFoundError(f"EcoPass {id}를 찾을 수 없습니다")
```

예외는 자동으로 표준 에러 응답 형식으로 변환됩니다.

### Environment Configuration

`.env.example`을 복사하여 `.env` 파일 생성:
```bash
cp .env.example .env
```

**주요 환경 변수**:
- `DEBUG=true` - 핫 리로드 및 상세 에러 활성화
- `SUPABASE_URL` - Supabase 프로젝트 URL
- `SUPABASE_KEY` - Supabase API 키 (anon 또는 service key)
- `API_PREFIX=/api/v1` - API 경로 접두사

## 코드 예시 (Code Examples)

### 완전한 기능 추가 예시

**1. Entity (도메인 엔티티)**
```python
# src/domain/entities/activity.py
from sqlmodel import Field, SQLModel

class Activity(SQLModel, table=True):
    """사용자 활동 엔티티"""
    __tablename__ = "activities"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True)
    activity_type: str = Field(max_length=50)
    points: int = Field(ge=0)
```

**2. Request/Response Schemas**
```python
# src/api/schemas/activity_schemas.py
from src.shared.schemas.base import BaseRequest, BaseResponse

class CreateActivityRequest(BaseRequest):
    """활동 생성 요청"""
    user_id: str
    activity_type: str

class ActivityResponse(BaseResponse):
    """활동 응답"""
    id: UUID
    user_id: str
    activity_type: str
    points: int
```

**3. API Route**
```python
# src/api/routes/activity_routes.py
from fastapi import APIRouter
from src.shared.schemas.response import SuccessResponse

router = APIRouter(prefix="/activities", tags=["Activities"])

@router.post("", response_model=SuccessResponse[ActivityResponse])
async def create_activity(request: CreateActivityRequest):
    """활동 생성 엔드포인트"""
    # 서비스 호출
    activity = await activity_service.create(request)
    return SuccessResponse.create(
        message="활동이 생성되었습니다",
        data=ActivityResponse.model_validate(activity)
    )
```

## Development Notes

### uv 패키지 매니저

이 프로젝트는 pip/poetry/pipenv 대신 `uv`를 사용합니다:
- 훨씬 빠른 의존성 해결 및 설치
- 표준 `pyproject.toml` 형식과 호환
- 가상 환경 자동 생성 및 관리
- Python 명령어 실행 시 항상 `uv run` 접두사 사용

### Repository Pattern

현재는 데모용 인메모리 레포지토리(`InMemoryEcoPassRepository`)를 사용 중입니다.
Supabase 프로덕션 사용 시:
1. `SupabaseEcoPassRepository` 생성하여 `IEcoPassRepository` 구현
2. `src/api/dependencies/`에서 의존성 주입 업데이트
3. 도메인, 애플리케이션, API 계층은 변경 불필요 (DDD의 이점)

### Testing Strategy

향후 테스트 추가 시:
- **단위 테스트**: 도메인 엔티티와 서비스
- **통합 테스트**: 레포지토리 (테스트용 Supabase 인스턴스 사용)
- **API 테스트**: 엔드포인트 (FastAPI TestClient 사용)

## 체크리스트 (Checklist)

새로운 기능을 추가할 때 다음을 확인하세요:

- [ ] SQLModel 엔티티에 `table=True` 설정
- [ ] Request 스키마는 `~~Request`, Response는 `~~Response` 명명
- [ ] BaseRequest, BaseResponse 상속
- [ ] 모든 클래스와 함수에 한글 주석 1-2줄
- [ ] 커스텀 예외는 BaseAppException 계열 사용
- [ ] 표준 응답 형식 사용 (`SuccessResponse.create()`)
- [ ] 불필요한 try-catch 제거
- [ ] 미래를 위한 코드 작성 금지 (YAGNI)
