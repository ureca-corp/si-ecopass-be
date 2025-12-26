"""
Trip Dependencies

FastAPI 의존성 주입을 위한 여행 관련 함수
Trip 레포지토리와 서비스 인스턴스 제공
"""

from fastapi import Depends
from supabase import Client

from src.application.services.trip_service import TripService
from src.domain.repositories.trip_repository import ITripRepository
from src.infrastructure.database.supabase import get_db
from src.infrastructure.repositories.trip_repository_impl import SupbaseTripRepository


def get_trip_repository(db: Client = Depends(get_db)) -> ITripRepository:
    """
    Trip Repository 의존성 주입
    Supabase 기반 레포지토리 구현체 반환
    """
    return SupbaseTripRepository(db)


def get_trip_service(
    trip_repository: ITripRepository = Depends(get_trip_repository),
) -> TripService:
    """
    Trip Service 의존성 주입
    FastAPI 엔드포인트에서 TripService를 사용할 수 있도록 제공
    """
    return TripService(trip_repository)
