"""
Station Repository Supabase Implementation

Supabase를 사용한 지하철 역 및 주차장 데이터 접근 구현
PostGIS 좌표 처리를 위해 Supabase RPC 함수 활용
"""

from typing import Optional
from uuid import UUID

from supabase import Client

from src.domain.entities.parking_lot import ParkingLot
from src.domain.entities.station import Station
from src.domain.repositories.station_repository import IStationRepository


class SupabaseStationRepository(IStationRepository):
    """
    Supabase를 사용한 Station Repository 구현

    PostGIS geography(Point) 타입의 좌표를 처리하여 latitude/longitude 제공
    Supabase의 database view 또는 RPC 함수를 통해 좌표 변환
    """

    def __init__(self, db: Client):
        self.db = db

    def _parse_station_data(self, row: dict) -> Station:
        """
        Supabase 응답 데이터를 Station 엔티티로 변환
        좌표 데이터는 latitude/longitude 필드로 제공
        """
        return Station(
            id=row.get("id"),
            name=row.get("name"),
            line_number=row.get("line_number"),
            latitude=row.get("latitude"),
            longitude=row.get("longitude"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    def _parse_parking_lot_data(self, row: dict) -> ParkingLot:
        """
        Supabase 응답 데이터를 ParkingLot 엔티티로 변환
        좌표 데이터는 latitude/longitude 필드로 제공
        """
        return ParkingLot(
            id=row.get("id"),
            station_id=row.get("station_id"),
            name=row.get("name"),
            address=row.get("address"),
            latitude=row.get("latitude"),
            longitude=row.get("longitude"),
            distance_to_station_m=row.get("distance_to_station_m"),
            fee_info=row.get("fee_info"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    async def get_all(
        self,
        line_number: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[Station]:
        """
        모든 지하철 역 조회 (선택적으로 노선별 필터링 및 페이지네이션)

        Supabase에 stations_view라는 View를 생성하여 사용하거나
        RPC 함수 get_stations_with_coords()를 호출
        """
        # Supabase RPC 함수 호출 (PostGIS 좌표 변환 포함)
        try:
            # RPC 함수가 있다면 사용
            params = {}
            if line_number is not None:
                params["p_line_number"] = line_number
            if limit is not None:
                params["p_limit"] = limit
            if offset is not None:
                params["p_offset"] = offset
            response = self.db.rpc("get_stations_with_coords", params).execute()
            return [self._parse_station_data(row) for row in response.data]
        except Exception:
            # RPC 함수가 없으면 일반 테이블 조회 (좌표는 null)
            query = self.db.table("stations").select("*")

            if line_number is not None:
                query = query.eq("line_number", line_number)

            query = query.order("name")

            if limit is not None:
                query = query.limit(limit)

            if offset is not None:
                query = query.range(offset, offset + (limit or 100) - 1)

            response = query.execute()

            # 좌표 정보는 없지만 기본 데이터 반환
            return [self._parse_station_data(row) for row in response.data]

    async def get_by_id(self, station_id: UUID) -> Optional[Station]:
        """
        ID로 특정 역 조회
        """
        try:
            # RPC 함수 사용
            response = self.db.rpc(
                "get_station_by_id_with_coords", {"p_station_id": str(station_id)}
            ).execute()

            if not response.data:
                return None

            return self._parse_station_data(response.data[0])
        except Exception:
            # RPC 함수가 없으면 일반 조회
            response = self.db.table("stations").select("*").eq("id", str(station_id)).execute()

            if not response.data:
                return None

            return self._parse_station_data(response.data[0])

    async def get_parking_lots(self, station_id: UUID) -> list[ParkingLot]:
        """
        특정 역의 주차장 목록 조회
        """
        try:
            # RPC 함수 사용
            response = self.db.rpc(
                "get_parking_lots_with_coords", {"p_station_id": str(station_id)}
            ).execute()

            return [self._parse_parking_lot_data(row) for row in response.data]
        except Exception:
            # RPC 함수가 없으면 일반 조회
            response = (
                self.db.table("parking_lots")
                .select("*")
                .eq("station_id", str(station_id))
                .order("distance_to_station_m")
                .execute()
            )

            return [self._parse_parking_lot_data(row) for row in response.data]
