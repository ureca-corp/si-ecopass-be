"""
Supabase 클라이언트 설정

Supabase 연결 및 클라이언트 인스턴스 관리
"""

from functools import lru_cache

from supabase import Client, create_client

from src.config import get_settings


@lru_cache
def get_supabase_client() -> Client:
    """
    Supabase 클라이언트 인스턴스 반환 (싱글톤)
    설정에서 URL과 키를 가져와 클라이언트 생성
    """
    settings = get_settings()

    if not settings.supabase_url or not settings.supabase_key:
        raise ValueError("Supabase URL과 KEY가 환경 변수에 설정되어야 합니다")

    # Storage API는 URL 끝에 슬래시가 필요함
    supabase_url = settings.supabase_url.rstrip("/") + "/"

    return create_client(supabase_url, settings.supabase_key)


def get_db() -> Client:
    """
    FastAPI 의존성 주입용 Supabase 클라이언트 제공
    각 요청마다 동일한 클라이언트 인스턴스 재사용
    """
    return get_supabase_client()
