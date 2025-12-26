"""
Storage Dependencies

FastAPI 의존성 주입을 위한 스토리지 관련 함수
StorageService 인스턴스 제공
"""

from fastapi import Depends
from supabase import Client

from src.application.services.storage_service import StorageService
from src.infrastructure.database.supabase import get_db


def get_storage_service(db: Client = Depends(get_db)) -> StorageService:
    """
    StorageService 의존성 주입
    FastAPI 엔드포인트에서 StorageService를 사용할 수 있도록 제공
    """
    return StorageService(db)
