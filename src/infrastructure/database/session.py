"""
SQLModel Session 설정

SQLModel을 사용한 데이터베이스 연결 및 세션 관리
FastAPI 의존성 주입용 Session 팩토리 제공
"""

from typing import Generator

from sqlmodel import Session, create_engine

from src.config import get_settings

# 전역 Engine 인스턴스 (앱 시작 시 초기화)
_engine = None


def init_db() -> None:
    """
    데이터베이스 Engine 초기화
    애플리케이션 시작 시 한 번만 호출
    """
    global _engine

    settings = get_settings()

    if not settings.database_url:
        raise ValueError("DATABASE_URL이 환경 변수에 설정되어야 합니다")

    # PostgreSQL 연결 풀 설정
    _engine = create_engine(
        settings.database_url,
        echo=settings.debug,  # 디버그 모드에서 SQL 쿼리 로깅
        pool_pre_ping=True,  # 연결 유효성 사전 체크
        pool_size=5,  # 기본 연결 풀 크기
        max_overflow=10,  # 최대 추가 연결 수
    )


def get_engine():
    """
    Engine 인스턴스 반환
    init_db()가 먼저 호출되어야 함
    """
    if _engine is None:
        raise RuntimeError("Database engine not initialized. Call init_db() first.")
    return _engine


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI 의존성 주입용 Session 제공
    요청마다 새로운 세션을 생성하고 자동으로 종료

    사용 예:
    ```python
    @app.get("/users")
    def get_users(session: Session = Depends(get_session)):
        users = session.exec(select(User)).all()
        return users
    ```
    """
    engine = get_engine()
    with Session(engine) as session:
        yield session


def close_db() -> None:
    """
    데이터베이스 연결 종료
    애플리케이션 종료 시 호출
    """
    global _engine
    if _engine:
        _engine.dispose()
        _engine = None
