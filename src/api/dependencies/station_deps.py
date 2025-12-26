"""
Station Dependencies

FastAPI dependency injection for Station services
"""

from typing import Annotated

from fastapi import Depends
from supabase import Client

from src.application.services.station_service import StationService
from src.domain.repositories.station_repository import IStationRepository
from src.infrastructure.database.supabase import get_db
from src.infrastructure.repositories.station_repository_impl import SupabaseStationRepository


def get_station_repository(
    db: Annotated[Client, Depends(get_db)],
) -> IStationRepository:
    """
    Station Repository 인스턴스 생성
    Supabase 클라이언트를 의존성으로 주입받아 레포지토리 생성
    """
    return SupabaseStationRepository(db=db)


def get_station_service(
    repository: Annotated[IStationRepository, Depends(get_station_repository)],
) -> StationService:
    """
    Station Service 인스턴스 생성
    Repository를 의존성으로 주입받아 서비스 생성
    """
    return StationService(repository=repository)
