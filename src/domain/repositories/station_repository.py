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
    async def get_all(
        self,
        line_number: Optional[int] = None,
        keyword: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[Station]:
        """
        모든 지하철 역 조회 (선택적으로 노선별 필터링, 키워드 검색 및 페이지네이션)

        Args:
            line_number: 노선 번호 (1, 2, 3, 4) - None이면 전체 조회
            keyword: 역 이름 검색 키워드 (부분 일치)
            limit: 반환할 결과 수
            offset: 건너뛸 결과 수

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

    @abstractmethod
    async def get_all_parking_lots(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[ParkingLot]:
        """
        전체 주차장 목록 조회 (페이지네이션 지원)

        Args:
            limit: 반환할 결과 수
            offset: 건너뛸 결과 수

        Returns:
            ParkingLot 엔티티 리스트
        """
        pass

    @abstractmethod
    async def get_parking_lot_by_id(self, parking_lot_id: UUID) -> Optional[ParkingLot]:
        """
        ID로 특정 주차장 조회

        Args:
            parking_lot_id: 주차장 고유 식별자

        Returns:
            ParkingLot 엔티티 또는 None
        """
        pass

    # ========================================================================
    # 관리자용 CRUD 메서드
    # ========================================================================

    @abstractmethod
    async def create_station(
        self, name: str, line_number: int, latitude: float, longitude: float
    ) -> Station:
        """새 역 생성"""
        pass

    @abstractmethod
    async def update_station(
        self,
        station_id: UUID,
        name: Optional[str] = None,
        line_number: Optional[int] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Station:
        """역 정보 수정"""
        pass

    @abstractmethod
    async def delete_station(self, station_id: UUID) -> None:
        """역 삭제"""
        pass

    @abstractmethod
    async def create_parking_lot(
        self,
        station_id: UUID,
        name: str,
        address: str,
        latitude: float,
        longitude: float,
        distance_to_station_m: Optional[int] = None,
        fee_info: Optional[str] = None,
    ) -> ParkingLot:
        """새 주차장 생성"""
        pass

    @abstractmethod
    async def update_parking_lot(
        self,
        parking_lot_id: UUID,
        station_id: Optional[UUID] = None,
        name: Optional[str] = None,
        address: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        distance_to_station_m: Optional[int] = None,
        fee_info: Optional[str] = None,
    ) -> ParkingLot:
        """주차장 정보 수정"""
        pass

    @abstractmethod
    async def delete_parking_lot(self, parking_lot_id: UUID) -> None:
        """주차장 삭제"""
        pass
