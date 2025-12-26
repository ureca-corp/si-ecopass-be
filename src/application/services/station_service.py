"""
Station Application Service

지하철 역 및 주차장 조회 비즈니스 로직을 조율하는 서비스
"""

from typing import Optional
from uuid import UUID

from src.domain.entities.parking_lot import ParkingLot
from src.domain.entities.station import Station
from src.domain.repositories.station_repository import IStationRepository
from src.shared.exceptions import NotFoundError


class StationService:
    """
    Station Application Service

    역 및 주차장 조회 유스케이스 구현
    """

    def __init__(self, repository: IStationRepository):
        self.repository = repository

    async def get_all_stations(
        self,
        line_number: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[Station]:
        """
        지하철 역 목록 조회 (선택적 노선 필터링 및 페이지네이션)

        Args:
            line_number: 노선 번호 (1, 2, 3) - None이면 전체 조회
            limit: 반환할 결과 수
            offset: 건너뛸 결과 수

        Returns:
            Station 엔티티 리스트
        """
        return await self.repository.get_all(line_number=line_number, limit=limit, offset=offset)

    async def get_station_by_id(self, station_id: UUID) -> Station:
        """
        특정 역 상세 조회

        Args:
            station_id: 역 고유 식별자

        Returns:
            Station 엔티티

        Raises:
            NotFoundError: 역을 찾을 수 없을 때
        """
        station = await self.repository.get_by_id(station_id)
        if not station:
            raise NotFoundError(f"역 ID {station_id}를 찾을 수 없습니다")
        return station

    async def get_station_parking_lots(self, station_id: UUID) -> list[ParkingLot]:
        """
        특정 역의 주차장 목록 조회

        Args:
            station_id: 역 고유 식별자

        Returns:
            ParkingLot 엔티티 리스트

        Raises:
            NotFoundError: 역을 찾을 수 없을 때
        """
        # 역 존재 여부 확인
        await self.get_station_by_id(station_id)

        # 주차장 목록 조회
        return await self.repository.get_parking_lots(station_id)
