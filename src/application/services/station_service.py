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
        keyword: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[Station]:
        """
        지하철 역 목록 조회 (선택적 노선 필터링, 키워드 검색 및 페이지네이션)

        Args:
            line_number: 노선 번호 (1, 2, 3, 4) - None이면 전체 조회
            keyword: 역 이름 검색 키워드 (부분 일치)
            limit: 반환할 결과 수
            offset: 건너뛸 결과 수

        Returns:
            Station 엔티티 리스트
        """
        return await self.repository.get_all(
            line_number=line_number, keyword=keyword, limit=limit, offset=offset
        )

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
        return await self.repository.get_all_parking_lots(limit=limit, offset=offset)

    async def get_parking_lot_by_id(self, parking_lot_id: UUID) -> ParkingLot:
        """
        특정 주차장 상세 조회

        Args:
            parking_lot_id: 주차장 고유 식별자

        Returns:
            ParkingLot 엔티티

        Raises:
            NotFoundError: 주차장을 찾을 수 없을 때
        """
        parking_lot = await self.repository.get_parking_lot_by_id(parking_lot_id)
        if not parking_lot:
            raise NotFoundError(f"주차장 ID {parking_lot_id}를 찾을 수 없습니다")
        return parking_lot

    # ========================================================================
    # 관리자용 CRUD 메서드
    # ========================================================================

    async def create_station(
        self,
        name: str,
        line_number: int,
        latitude: float,
        longitude: float,
    ) -> Station:
        """
        새 역 생성

        Args:
            name: 역 이름
            line_number: 노선 번호 (1, 2, 3, 4)
            latitude: 위도
            longitude: 경도

        Returns:
            생성된 Station 엔티티
        """
        return await self.repository.create_station(
            name=name,
            line_number=line_number,
            latitude=latitude,
            longitude=longitude,
        )

    async def update_station(
        self,
        station_id: UUID,
        name: Optional[str] = None,
        line_number: Optional[int] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
    ) -> Station:
        """
        역 정보 수정

        Args:
            station_id: 역 ID
            name, line_number, latitude, longitude: 수정할 필드 (None이면 변경 안함)

        Returns:
            수정된 Station 엔티티
        """
        # 역 존재 여부 확인
        await self.get_station_by_id(station_id)

        return await self.repository.update_station(
            station_id=station_id,
            name=name,
            line_number=line_number,
            latitude=latitude,
            longitude=longitude,
        )

    async def delete_station(self, station_id: UUID) -> None:
        """
        역 삭제 (연결된 주차장도 함께 삭제됨 - CASCADE)

        Args:
            station_id: 역 ID
        """
        # 역 존재 여부 확인
        await self.get_station_by_id(station_id)

        await self.repository.delete_station(station_id)

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
        """
        새 주차장 생성

        Args:
            station_id: 연계 역 ID
            name: 주차장 이름
            address: 주소
            latitude, longitude: GPS 좌표
            distance_to_station_m: 역까지 거리 (미터)
            fee_info: 요금 정보

        Returns:
            생성된 ParkingLot 엔티티
        """
        # 역 존재 여부 확인
        await self.get_station_by_id(station_id)

        return await self.repository.create_parking_lot(
            station_id=station_id,
            name=name,
            address=address,
            latitude=latitude,
            longitude=longitude,
            distance_to_station_m=distance_to_station_m,
            fee_info=fee_info,
        )

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
        """
        주차장 정보 수정

        Args:
            parking_lot_id: 주차장 ID
            기타 필드: 수정할 값 (None이면 변경 안함)

        Returns:
            수정된 ParkingLot 엔티티
        """
        # station_id 변경 시 새 역 존재 확인
        if station_id:
            await self.get_station_by_id(station_id)

        return await self.repository.update_parking_lot(
            parking_lot_id=parking_lot_id,
            station_id=station_id,
            name=name,
            address=address,
            latitude=latitude,
            longitude=longitude,
            distance_to_station_m=distance_to_station_m,
            fee_info=fee_info,
        )

    async def delete_parking_lot(self, parking_lot_id: UUID) -> None:
        """
        주차장 삭제

        Args:
            parking_lot_id: 주차장 ID
        """
        await self.repository.delete_parking_lot(parking_lot_id)
