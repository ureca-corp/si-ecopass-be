# SI-EcoPass Backend API

> 대구 지하철 환승 주차장 이용 장려 플랫폼의 백엔드 API

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg)](https://supabase.com/)

---

## 📋 프로젝트 개요

SI-EcoPass는 대구 지하철 이용자들이 환승 주차장을 활용하여 대중교통 이용을 장려하는 플랫폼입니다.

**핵심 기능:**
- 🔐 사용자 인증 (JWT + Supabase Auth)
- 🚇 역 및 주차장 조회 (PostGIS 기반 위치 검색)
- 🚗 여정 관리 (출발 → 환승 → 도착)
- 📷 이미지 업로드 (Supabase Storage)
- 👮 관리자 승인 및 포인트 지급

**기술 스택:**
- Python 3.12+ | FastAPI | SQLModel
- Supabase (PostgreSQL + PostGIS + Auth + Storage)
- Domain-Driven Design (DDD)

---

## 📦 프로젝트 구조

```
src/
├── domain/              # 도메인 계층 (엔티티, 비즈니스 로직)
├── application/         # 애플리케이션 계층 (서비스, 유스케이스)
├── infrastructure/      # 인프라 계층 (DB, 외부 API)
├── api/                 # API 계층 (라우터, 스키마)
└── shared/              # 공유 커널 (예외, 유틸)

tests/                   # 테스트 코드
supabase/migrations/     # 데이터베이스 마이그레이션
```

---

## 🚀 빠른 시작

### 1. 설치

```bash
# 1. 저장소 클론
git clone https://github.com/your-org/si-ecopass-be.git
cd si-ecopass-be

# 2. uv 설치 (Python 패키지 매니저)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. 의존성 설치
uv sync
```

### 2. 환경 변수 설정

```bash
# .env.example을 복사하여 .env 생성
cp .env.example .env
```

**`.env` 파일 수정:**
```bash
# Supabase 설정 (https://supabase.com 에서 프로젝트 생성 후 확인)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here

# Database URL (Supabase Dashboard > Project Settings > Database)
DATABASE_URL=postgresql://postgres:your_password@db.your_project_id.supabase.co:5432/postgres

# 개발 환경
DEBUG=true
ENVIRONMENT=development
```

**비밀 키 가져오기:**
1. [Supabase Dashboard](https://supabase.com/dashboard) 로그인
2. 프로젝트 선택 → **Settings** → **API**
3. **Project URL** → `SUPABASE_URL`에 복사
4. **anon public** 키 → `SUPABASE_KEY`에 복사
5. **Settings** → **Database** → **Connection string** → URI 복사 → `DATABASE_URL`에 복사

### 3. 데이터베이스 초기화

Supabase Dashboard에서 `supabase/migrations/*.sql` 파일들을 순서대로 실행:
```
1. 20251226000001_create_initial_schema.sql
2. 20251226000002_add_user_role.sql
```

### 4. 서버 실행

```bash
# 개발 모드 (핫 리로드)
uv run python main.py

# 테스트 실행
uv run pytest

# API 문서 확인
# http://localhost:8000/docs
```

---

## 📖 API 문서

서버 실행 후 확인:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📞 지원

- [GitHub Issues](https://github.com/your-org/si-ecopass-be/issues)
- Email: support@siecopass.com
- 상세 문서: `CLAUDE.md` 참조

---

**Happy Coding! 🚀**
