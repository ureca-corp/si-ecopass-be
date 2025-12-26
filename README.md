# SI-EcoPass Backend API

> 대구 지하철 환승 주차장 이용 장려 플랫폼의 백엔드 API

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg)](https://supabase.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

---

## 📋 프로젝트 개요

SI-EcoPass는 대구 지하철 이용자들이 환승 주차장을 활용하여 대중교통 이용을 장려하는 플랫폼입니다. 사용자는 출발지 주차 → 지하철 환승 → 목적지 도착의 여정을 기록하고, 관리자 승인 후 환경 포인트를 획득할 수 있습니다.

### 핵심 가치
- **환경 보호**: 승용차 대신 대중교통 이용 장려
- **주차 편의성**: 환승 주차장 정보 제공
- **포인트 시스템**: 친환경 활동 보상

---

## 🎯 주요 기능

### 1. 🔐 사용자 인증
- JWT 기반 회원가입, 로그인
- 프로필 조회 및 수정
- Supabase Auth 통합

### 2. 🚇 역 및 주차장 조회
- 대구 지하철 1/2/3호선 역 정보
- 각 역별 주변 환승 주차장 정보
- 위치 기반 주변 역 검색 (PostGIS)

### 3. 🚗 여정 관리
- **3단계 프로세스**: 출발 (DRIVING) → 환승 (TRANSFERRED) → 도착 (COMPLETED)
- 각 단계별 위치 정보 기록
- 환승/도착 증빙 이미지 업로드

### 4. 📷 이미지 스토리지
- Supabase Storage 통합
- 환승/도착 증빙 사진 업로드
- 자동 파일명 생성 및 URL 반환

### 5. 👮 관리자 기능
- 완료된 여정 승인/반려
- 포인트 지급
- 전체 여정 목록 조회 및 필터링

---

## 🛠️ 기술 스택

### Backend
- **Language**: Python 3.12+
- **Framework**: FastAPI 0.115+
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Package Manager**: uv

### Database & Services
- **Database**: Supabase (PostgreSQL 15+ with PostGIS)
- **Authentication**: Supabase Auth (JWT)
- **Storage**: Supabase Storage
- **Realtime**: Supabase Realtime (선택적)

### Architecture
- **Pattern**: Domain-Driven Design (DDD)
- **Layers**: Domain → Application → Infrastructure → API

### Testing
- **Framework**: pytest, pytest-asyncio
- **Coverage**: pytest-cov
- **Client**: FastAPI TestClient

---

## 📚 API 문서

### 로컬 개발 환경
서버 실행 후 다음 URL에서 API 문서 확인:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Postman Collection
프로젝트 루트의 `postman/` 디렉토리에서 Postman Collection 제공

---

## 🚀 로컬 개발 가이드

### 1. Prerequisites

다음 도구들이 설치되어 있어야 합니다:

- **Python 3.12 이상**
- **uv** (Python 패키지 매니저)
  ```bash
  # macOS/Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **Supabase 계정** (프로젝트 생성 필요)

### 2. Installation

```bash
# 1. 저장소 클론
git clone https://github.com/your-org/si-ecopass-be.git
cd si-ecopass-be

# 2. 의존성 설치
uv sync

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 Supabase 정보 입력

# 4. Supabase 초기 설정 (테이블 생성)
# Supabase Dashboard에서 supabase/migrations/*.sql 실행
```

### 3. 환경 변수 설정 (.env)

```bash
# 애플리케이션 설정
APP_NAME="SI-EcoPass Backend"
APP_VERSION="1.0.0"
DEBUG=true
ENVIRONMENT=development

# API 설정
API_PREFIX=/api/v1
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Supabase 연결 정보
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

# Uvicorn 서버 설정
HOST=0.0.0.0
PORT=8000
```

### 4. Running the Server

```bash
# 개발 모드 (핫 리로드)
uv run python main.py

# 또는 uvicorn 직접 실행
uv run uvicorn src.main:app --reload

# 프로덕션 모드 (리로드 없음)
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

서버가 시작되면 http://localhost:8000 에서 API에 접근할 수 있습니다.

### 5. Running Tests

```bash
# 전체 테스트 실행
uv run pytest

# 커버리지 리포트와 함께 실행
uv run pytest --cov=src --cov-report=html

# 특정 테스트 파일만 실행
uv run pytest tests/test_auth.py

# 상세 출력 모드
uv run pytest -v

# 특정 테스트 케이스만 실행
uv run pytest tests/test_auth.py::TestSignup::test_signup_success
```

테스트 커버리지 리포트는 `htmlcov/index.html`에서 확인 가능합니다.

---

## 📖 API 엔드포인트

### Authentication (`/api/v1/auth`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/signup` | 회원가입 | ❌ |
| POST | `/login` | 로그인 | ❌ |
| GET | `/profile` | 프로필 조회 | ✅ |
| PUT | `/profile` | 프로필 수정 | ✅ |

### Stations (`/api/v1/stations`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | 전체 역 목록 조회 | ❌ |
| GET | `/{station_id}` | 역 상세 정보 조회 | ❌ |
| GET | `/{station_id}/parking-lots` | 역별 주차장 목록 | ❌ |
| GET | `/nearby` | 주변 역 검색 | ❌ |

### Trips (`/api/v1/trips`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/start` | 여정 시작 | ✅ |
| POST | `/{trip_id}/transfer` | 환승 기록 | ✅ |
| POST | `/{trip_id}/arrival` | 도착 기록 | ✅ |
| GET | `/` | 내 여정 목록 조회 | ✅ |
| GET | `/{trip_id}` | 여정 상세 정보 조회 | ✅ |

### Storage (`/api/v1/storage`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/upload/transfer` | 환승 이미지 업로드 | ✅ |
| POST | `/upload/arrival` | 도착 이미지 업로드 | ✅ |

### Admin (`/api/v1/admin`)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/trips` | 전체 여정 목록 조회 | 👮 Admin |
| POST | `/trips/{trip_id}/approve` | 여정 승인 | 👮 Admin |
| POST | `/trips/{trip_id}/reject` | 여정 반려 | 👮 Admin |

---

## 🔒 인증 방법

모든 인증이 필요한 엔드포인트는 JWT Bearer Token을 사용합니다.

### 1. 로그인하여 토큰 획득

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**응답:**
```json
{
  "status": "success",
  "message": "로그인 성공",
  "data": {
    "user": { ... },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

### 2. 요청 헤더에 토큰 추가

```bash
GET /api/v1/auth/profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## ⚠️ 에러 코드

모든 에러는 표준 HTTP 상태 코드와 함께 다음 형식으로 반환됩니다:

```json
{
  "status": "error",
  "message": "에러 메시지",
  "data": null
}
```

| 코드 | 설명 | 예시 |
|------|------|------|
| 400 | Bad Request | 잘못된 요청 파라미터 |
| 401 | Unauthorized | 인증 토큰 없음 또는 만료 |
| 403 | Forbidden | 권한 없음 (관리자 전용 API 등) |
| 404 | Not Found | 리소스를 찾을 수 없음 |
| 409 | Conflict | 리소스 충돌 (중복 이메일, 진행 중 여정) |
| 422 | Unprocessable Entity | 유효성 검증 실패 |
| 500 | Internal Server Error | 서버 내부 오류 |

---

## 🧪 테스트

### 테스트 구조

```
tests/
├── conftest.py              # pytest fixtures
├── test_auth.py             # 인증 API 테스트
├── test_stations.py         # 역/주차장 API 테스트
├── test_trips.py            # 여정 관리 API 테스트
├── test_storage.py          # 이미지 업로드 API 테스트
├── test_admin.py            # 관리자 API 테스트
└── test_integration.py      # 통합 시나리오 테스트
```

### 테스트 커버리지 목표

- **Domain entities and business logic**: 80%+
- **API endpoints**: 90%+
- **Core business logic**: 100%

### 테스트 실행 명령어

```bash
# 전체 테스트
uv run pytest

# 특정 카테고리만
uv run pytest tests/test_auth.py

# 커버리지 확인
uv run pytest --cov=src --cov-report=term-missing

# HTML 커버리지 리포트
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## 📦 프로젝트 구조

```
si-ecopass-be/
├── src/
│   ├── domain/              # 도메인 계층 (비즈니스 로직)
│   │   ├── entities/        # 도메인 엔티티 (SQLModel)
│   │   ├── repositories/    # 레포지토리 인터페이스
│   │   └── value_objects/   # 값 객체
│   ├── application/         # 애플리케이션 계층 (유스케이스)
│   │   ├── services/        # 애플리케이션 서비스
│   │   └── use_cases/       # 유스케이스 구현
│   ├── infrastructure/      # 인프라 계층 (외부 시스템)
│   │   ├── database/        # Supabase 클라이언트
│   │   ├── repositories/    # 레포지토리 구현
│   │   └── external/        # 외부 서비스 연동
│   ├── api/                 # API 계층 (프레젠테이션)
│   │   ├── routes/          # FastAPI 라우터
│   │   ├── schemas/         # Request/Response DTO
│   │   └── dependencies/    # 의존성 주입
│   ├── shared/              # 공유 커널
│   │   ├── schemas/         # 공통 스키마
│   │   ├── utils/           # 유틸리티 함수
│   │   └── exceptions.py    # 커스텀 예외
│   ├── config.py            # 설정 관리
│   └── main.py              # FastAPI 앱 팩토리
├── tests/                   # 테스트 코드
├── supabase/                # Supabase 마이그레이션
├── postman/                 # Postman Collection
├── .env.example             # 환경 변수 예시
├── pytest.ini               # pytest 설정
├── pyproject.toml           # 프로젝트 메타데이터
└── README.md                # 이 파일
```

---

## 🏗️ 아키텍처 원칙

### Domain-Driven Design (DDD)

이 프로젝트는 DDD 원칙을 따릅니다:

1. **Domain Layer** (도메인 계층)
   - 순수한 비즈니스 로직
   - 외부 의존성 없음
   - SQLModel 엔티티 정의

2. **Application Layer** (애플리케이션 계층)
   - 도메인 객체 조율
   - 유스케이스 구현
   - 트랜잭션 관리

3. **Infrastructure Layer** (인프라 계층)
   - 데이터베이스 연동 (Supabase)
   - 외부 API 클라이언트
   - 레포지토리 구현

4. **API Layer** (API 계층)
   - HTTP 엔드포인트
   - Request/Response 변환
   - 의존성 주입

### 의존성 규칙

**의존성 방향**: API → Application → Domain

- Domain은 외부 계층을 모름
- Application은 Domain만 의존
- Infrastructure는 Domain 인터페이스 구현
- API는 Application을 사용

---

## 📝 표준 응답 형식

모든 API 응답은 다음 형식을 따릅니다:

### 성공 응답
```json
{
  "status": "success",
  "message": "작업이 성공했습니다",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "field": "value"
  }
}
```

### 에러 응답
```json
{
  "status": "error",
  "message": "에러 메시지",
  "data": null
}
```

---

## 🚢 배포

### 환경별 설정

- **Development**: `DEBUG=true`, 상세 에러 메시지
- **Production**: `DEBUG=false`, 일반 에러 메시지

### 프로덕션 체크리스트

- [ ] `.env` 파일에 프로덕션 Supabase 키 설정
- [ ] `DEBUG=false` 설정
- [ ] CORS `ALLOWED_ORIGINS` 프로덕션 도메인 추가
- [ ] Supabase RLS (Row Level Security) 활성화
- [ ] 데이터베이스 마이그레이션 실행
- [ ] 환경 변수 보안 관리

---

## 👥 개발자

- **Project Lead**: SI-EcoPass Team
- **Backend Developer**: Your Name
- **Contact**: support@siecopass.com

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 관련 링크

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Supabase 공식 문서](https://supabase.com/docs)
- [SQLModel 공식 문서](https://sqlmodel.tiangolo.com/)
- [pytest 공식 문서](https://docs.pytest.org/)

---

## 📞 지원

문제가 발생하거나 질문이 있으시면:

1. [GitHub Issues](https://github.com/your-org/si-ecopass-be/issues) 생성
2. 이메일: support@siecopass.com
3. 프로젝트 Wiki 참조

---

**Happy Coding! 🚀**
