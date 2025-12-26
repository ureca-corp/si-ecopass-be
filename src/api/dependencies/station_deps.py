"""
Station Dependencies

FastAPI dependency injection for Station services
"""

from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from src.application.services.station_service import StationService
from src.domain.repositories.station_repository import IStationRepository
from src.infrastructure.database.session import get_session
from src.infrastructure.repositories.station_repository_impl import SQLModelStationRepository


def get_station_repository(
    session: Annotated[Session, Depends(get_session)],
) -> IStationRepository:
    """
    Station Repository 인스턴스 생성
    SQLModel Session을 의존성으로 주입받아 레포지토리 생성
    """
    return SQLModelStationRepository(session=session)


def get_station_service(
    repository: Annotated[IStationRepository, Depends(get_station_repository)],
) -> StationService:
    """
    Station Service 인스턴스 생성
    Repository를 의존성으로 주입받아 서비스 생성
    """
    return StationService(repository=repository)
