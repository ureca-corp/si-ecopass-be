"""
Station Repository Interface

지하철 역 및 주차장 데이터 접근을 위한 인터페이스 정의 (Repository Pattern)
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.domain.entities.parking_lot import ParkingLot
from src.domain.entities.station import Station


class IStationRepository(ABC):
    """
    Station Repository Interface

    도메인 레이어의 인터페이스 - 구현은 인프라 레이어에 위치
    """

    @abstractmethod
    async def get_all(self, line_number: Optional[int] = None) -> list[Station]:
        """
        모든 지하철 역 조회 (선택적으로 노선별 필터링)

        Args:
            line_number: 노선 번호 (1, 2, 3) - None이면 전체 조회

        Returns:
            Station 엔티티 리스트
        """
        pass

    @abstractmethod
    async def get_by_id(self, station_id: UUID) -> Optional[Station]:
        """
        ID로 특정 역 조회

        Args:
            station_id: 역 고유 식별자

        Returns:
            Station 엔티티 또는 None
        """
        pass

    @abstractmethod
    async def get_parking_lots(self, station_id: UUID) -> list[ParkingLot]:
        """
        특정 역의 주차장 목록 조회

        Args:
            station_id: 역 고유 식별자

        Returns:
            ParkingLot 엔티티 리스트
        """
        pass
