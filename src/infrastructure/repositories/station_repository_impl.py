"""
Station Repository SQLModel Implementation

SQLModel/SQLAlchemy를 사용한 지하철 역 및 주차장 데이터 접근 구현
PostGIS 좌표를 ORM으로 처리, latitude/longitude 컬럼과 트리거를 통한 좌표 관리
"""

from typing import Optional
from uuid import UUID

from geoalchemy2.functions import ST_X, ST_Y
from geoalchemy2.types import Geometry
from sqlalchemy import cast
from sqlmodel import Session, select

from src.domain.entities.parking_lot import ParkingLot
from src.domain.entities.station import Station
from src.domain.repositories.station_repository import IStationRepository


class SQLModelStationRepository(IStationRepository):
    """
    SQLModel/SQLAlchemy를 사용한 Station Repository 구현

    PostGIS geography(Point) 타입의 좌표를 ORM으로 처리하여 latitude/longitude 제공
    latitude/longitude 컬럼에 CRUD 수행 시 트리거가 location 자동 동기화
    """

    def __init__(self, session: Session):
        self.session = session

    async def get_all(
        self,
        line_number: Optional[int] = None,
        keyword: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[Station]:
        """
        모든 지하철 역 조회 (선택적으로 노선별 필터링, 키워드 검색 및 페이지네이션)
        PostGIS 좌표를 latitude/longitude로 변환하여 반환
        """
        stmt = select(
            Station.id,
            Station.name,
            Station.line_number,
            Station.created_at,
            ST_Y(cast(Station.location, Geometry)).label("latitude"),
            ST_X(cast(Station.location, Geometry)).label("longitude"),
        )

        if line_number is not None:
            stmt = stmt.where(Station.line_number == line_number)

        if keyword is not None:
            stmt = stmt.where(Station.name.ilike(f"%{keyword}%"))

        stmt = stmt.order_by(Station.name)

        if limit is not None:
            stmt = stmt.limit(limit)

        if offset is not None:
            stmt = stmt.offset(offset)

        result = self.session.exec(stmt)
        rows = result.all()

        return [
            Station(
                id=row.id,
                name=row.name,
                line_number=row.line_number,
                latitude=row.latitude,
                longitude=row.longitude,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def get_by_id(self, station_id: UUID) -> Optional[Station]:
        """ID로 특정 역 조회"""
        stmt = select(
            Station.id,
            Station.name,
            Station.line_number,
            Station.created_at,
            ST_Y(cast(Station.location, Geometry)).label("latitude"),
            ST_X(cast(Station.location, Geometry)).label("longitude"),
        ).where(Station.id == station_id)

        result = self.session.exec(stmt)
        row = result.first()

        if not row:
            return None

        return Station(
            id=row.id,
            name=row.name,
            line_number=row.line_number,
            latitude=row.latitude,
            longitude=row.longitude,
            created_at=row.created_at,
        )

    async def get_parking_lots(self, station_id: UUID) -> list[ParkingLot]:
        """특정 역의 주차장 목록 조회"""
        stmt = (
            select(
                ParkingLot.id,
                ParkingLot.station_id,
                ParkingLot.name,
                ParkingLot.address,
                ParkingLot.distance_to_station_m,
                ParkingLot.fee_info,
                ParkingLot.created_at,
                ST_Y(cast(ParkingLot.location, Geometry)).label("latitude"),
                ST_X(cast(ParkingLot.location, Geometry)).label("longitude"),
            )
            .where(ParkingLot.station_id == station_id)
            .order_by(ParkingLot.distance_to_station_m)
        )

        result = self.session.exec(stmt)
        rows = result.all()

        return [
            ParkingLot(
                id=row.id,
                station_id=row.station_id,
                name=row.name,
                address=row.address,
                latitude=row.latitude,
                longitude=row.longitude,
                distance_to_station_m=row.distance_to_station_m,
                fee_info=row.fee_info,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def get_all_parking_lots(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[ParkingLot]:
        """전체 주차장 목록 조회 (페이지네이션 지원)"""
        stmt = select(
            ParkingLot.id,
            ParkingLot.station_id,
            ParkingLot.name,
            ParkingLot.address,
            ParkingLot.distance_to_station_m,
            ParkingLot.fee_info,
            ParkingLot.created_at,
            ST_Y(cast(ParkingLot.location, Geometry)).label("latitude"),
            ST_X(cast(ParkingLot.location, Geometry)).label("longitude"),
        ).order_by(ParkingLot.name)

        if limit is not None:
            stmt = stmt.limit(limit)

        if offset is not None:
            stmt = stmt.offset(offset)

        result = self.session.exec(stmt)
        rows = result.all()

        return [
            ParkingLot(
                id=row.id,
                station_id=row.station_id,
                name=row.name,
                address=row.address,
                latitude=row.latitude,
                longitude=row.longitude,
                distance_to_station_m=row.distance_to_station_m,
                fee_info=row.fee_info,
                created_at=row.created_at,
            )
            for row in rows
        ]

    async def get_parking_lot_by_id(self, parking_lot_id: UUID) -> Optional[ParkingLot]:
        """ID로 특정 주차장 조회"""
        stmt = select(
            ParkingLot.id,
            ParkingLot.station_id,
            ParkingLot.name,
            ParkingLot.address,
            ParkingLot.distance_to_station_m,
            ParkingLot.fee_info,
            ParkingLot.created_at,
            ST_Y(cast(ParkingLot.location, Geometry)).label("latitude"),
            ST_X(cast(ParkingLot.location, Geometry)).label("longitude"),
        ).where(ParkingLot.id == parking_lot_id)

        result = self.session.exec(stmt)
        row = result.first()

        if not row:
            return None

        return ParkingLot(
            id=row.id,
            station_id=row.station_id,
            name=row.name,
            address=row.address,
            latitude=row.latitude,
            longitude=row.longitude,
            distance_to_station_m=row.distance_to_station_m,
            fee_info=row.fee_info,
            created_at=row.created_at,
        )

    # ========================================================================
    # 관리자용 CRUD 메서드
    # latitude/longitude 컬럼에 CRUD → 트리거가 location 자동 동기화
    # ========================================================================

    async def create_station(
        self, name: str, line_number: int, latitude: float, longitude: float
    ) -> Station:
        """
        새 역 생성
        lat/lng 삽입 시 PostgreSQL 트리거가 location(geography) 자동 생성
        """
        station = Station(
            name=name,
            line_number=line_number,
            latitude=latitude,
            longitude=longitude,
        )
        self.session.add(station)
        self.session.commit()
        self.session.refresh(station)
        return await self.get_by_id(station.id)

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
        lat/lng 업데이트 시 PostgreSQL 트리거가 location 자동 동기화
        """
        station = self.session.get(Station, station_id)
        if not station:
            return None

        if name is not None:
            station.name = name
        if line_number is not None:
            station.line_number = line_number
        if latitude is not None:
            station.latitude = latitude
        if longitude is not None:
            station.longitude = longitude

        self.session.add(station)
        self.session.commit()
        return await self.get_by_id(station_id)

    async def delete_station(self, station_id: UUID) -> None:
        """역 삭제 (CASCADE로 주차장도 함께 삭제)"""
        station = self.session.get(Station, station_id)
        if station:
            self.session.delete(station)
            self.session.commit()

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
        lat/lng 삽입 시 PostgreSQL 트리거가 location(geography) 자동 생성
        """
        parking_lot = ParkingLot(
            station_id=station_id,
            name=name,
            address=address,
            latitude=latitude,
            longitude=longitude,
            distance_to_station_m=distance_to_station_m,
            fee_info=fee_info,
        )
        self.session.add(parking_lot)
        self.session.commit()
        self.session.refresh(parking_lot)
        return parking_lot

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
        lat/lng 업데이트 시 PostgreSQL 트리거가 location 자동 동기화
        """
        parking_lot = self.session.get(ParkingLot, parking_lot_id)
        if not parking_lot:
            return None

        if station_id is not None:
            parking_lot.station_id = station_id
        if name is not None:
            parking_lot.name = name
        if address is not None:
            parking_lot.address = address
        if latitude is not None:
            parking_lot.latitude = latitude
        if longitude is not None:
            parking_lot.longitude = longitude
        if distance_to_station_m is not None:
            parking_lot.distance_to_station_m = distance_to_station_m
        if fee_info is not None:
            parking_lot.fee_info = fee_info

        self.session.add(parking_lot)
        self.session.commit()
        self.session.refresh(parking_lot)
        return parking_lot

    async def delete_parking_lot(self, parking_lot_id: UUID) -> None:
        """주차장 삭제"""
        parking_lot = self.session.get(ParkingLot, parking_lot_id)
        if parking_lot:
            self.session.delete(parking_lot)
            self.session.commit()
