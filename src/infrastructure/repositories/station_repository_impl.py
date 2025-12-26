"""
Station Repository SQLModel Implementation

SQLModel/SQLAlchemy를 사용한 지하철 역 및 주차장 데이터 접근 구현
PostGIS 좌표를 ORM으로 처리
"""

from typing import Optional
from uuid import UUID

from geoalchemy2.functions import ST_X, ST_Y
from sqlalchemy import cast, func
from sqlalchemy.types import Geometry
from sqlmodel import Session, select

from src.domain.entities.parking_lot import ParkingLot
from src.domain.entities.station import Station
from src.domain.repositories.station_repository import IStationRepository


class SQLModelStationRepository(IStationRepository):
    """
    SQLModel/SQLAlchemy를 사용한 Station Repository 구현

    PostGIS geography(Point) 타입의 좌표를 ORM으로 처리하여 latitude/longitude 제공
    """

    def __init__(self, session: Session):
        self.session = session

    async def get_all(
        self,
        line_number: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[Station]:
        """
        모든 지하철 역 조회 (선택적으로 노선별 필터링 및 페이지네이션)
        PostGIS 좌표를 latitude/longitude로 변환하여 반환
        """
        # ORM 쿼리 - PostGIS ST_X(), ST_Y() 함수로 좌표 추출
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

        stmt = stmt.order_by(Station.name)

        if limit is not None:
            stmt = stmt.limit(limit)

        if offset is not None:
            stmt = stmt.offset(offset)

        result = self.session.exec(stmt)
        rows = result.all()

        # 결과를 Station 엔티티로 변환
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
        """
        ID로 특정 역 조회
        """
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
        """
        특정 역의 주차장 목록 조회
        """
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
