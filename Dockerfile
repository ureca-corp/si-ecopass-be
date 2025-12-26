# ========================================
# Stage 1: Builder
# ========================================
FROM python:3.12-slim AS builder

# 빌드 인자 설정
ARG UV_VERSION=0.5.13

# 시스템 패키지 업데이트 및 필수 도구 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# uv 설치 (빠른 Python 패키지 관리자)
RUN curl -LsSf https://astral.sh/uv/${UV_VERSION}/install.sh | sh

# 환경 변수 설정
ENV PATH="/root/.local/bin:$PATH" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사
COPY pyproject.toml uv.lock ./

# 프로덕션 의존성 설치 (dev 제외)
RUN uv sync --frozen --no-dev --no-install-project


# ========================================
# Stage 2: Runtime
# ========================================
FROM python:3.12-slim

# 런타임 라이브러리 설치 (PostgreSQL 클라이언트)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

# 비-root 유저 생성 (보안)
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 -d /app -s /bin/bash appuser

# 작업 디렉토리 설정
WORKDIR /app

# Builder 스테이지에서 설치된 의존성 복사
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# 애플리케이션 소스 코드 복사
COPY --chown=appuser:appuser . .

# 환경 변수 설정
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production \
    DEBUG=False

# 포트 노출 (FastAPI 기본 포트)
EXPOSE 8000

# 비-root 유저로 전환
USER appuser

# Health check 설정
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=5.0)" || exit 1

# 애플리케이션 실행
CMD ["python", "main.py"]
