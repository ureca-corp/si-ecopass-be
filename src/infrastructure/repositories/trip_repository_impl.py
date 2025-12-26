"""
Trip Repository Supabase Implementation

Supabase를 사용한 여행 데이터 접근 구현
"""

from typing import Optional
from uuid import UUID

from supabase import Client

from src.domain.entities.trip import Trip, TripStatus
from src.domain.repositories.trip_repository import ITripRepository


class SupbaseTripRepository(ITripRepository):
    """
    Supabase를 사용한 Trip Repository 구현
    Supabase 테이블과 도메인 엔티티 간 변환 처리
    """

    def __init__(self, db: Client):
        self.db = db

    def _parse_trip_data(self, row: dict) -> Trip:
        """
        Supabase 응답 데이터를 Trip 엔티티로 변환
        """
        return Trip(
            id=row.get("id"),
            user_id=row.get("user_id"),
            start_latitude=row.get("start_latitude"),
            start_longitude=row.get("start_longitude"),
            transfer_latitude=row.get("transfer_latitude"),
            transfer_longitude=row.get("transfer_longitude"),
            transfer_image_url=row.get("transfer_image_url"),
            arrival_latitude=row.get("arrival_latitude"),
            arrival_longitude=row.get("arrival_longitude"),
            arrival_image_url=row.get("arrival_image_url"),
            status=TripStatus(row.get("status")),
            estimated_points=row.get("estimated_points"),
            earned_points=row.get("earned_points"),
            admin_note=row.get("admin_note"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    async def create(self, trip: Trip) -> Trip:
        """
        새로운 여행 생성
        """
        trip_data = trip.model_dump(mode="json")
        response = self.db.table("trips").insert(trip_data).execute()

        if not response.data:
            raise RuntimeError("여행 생성에 실패했습니다")

        return self._parse_trip_data(response.data[0])

    async def get_by_id(self, trip_id: UUID) -> Optional[Trip]:
        """
        ID로 특정 여행 조회
        """
        response = self.db.table("trips").select("*").eq("id", str(trip_id)).execute()

        if not response.data:
            return None

        return self._parse_trip_data(response.data[0])

    async def get_by_user_id(
        self,
        user_id: UUID,
        status: Optional[TripStatus] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Trip]:
        """
        사용자 ID로 여행 목록 조회
        상태별 필터링 및 페이지네이션 지원
        """
        query = self.db.table("trips").select("*").eq("user_id", str(user_id))

        if status is not None:
            query = query.eq("status", status.value)

        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        response = query.execute()

        return [self._parse_trip_data(row) for row in response.data]

    async def get_active_trip(self, user_id: UUID) -> Optional[Trip]:
        """
        사용자의 활성 여행 조회 (DRIVING 또는 TRANSFERRED)
        """
        response = (
            self.db.table("trips")
            .select("*")
            .eq("user_id", str(user_id))
            .in_("status", [TripStatus.DRIVING.value, TripStatus.TRANSFERRED.value])
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return self._parse_trip_data(response.data[0])

    async def update(self, trip: Trip) -> Trip:
        """
        여행 정보 업데이트
        """
        update_data = trip.model_dump(mode="json", exclude={"id", "user_id", "created_at"})
        response = self.db.table("trips").update(update_data).eq("id", str(trip.id)).execute()

        if not response.data:
            raise RuntimeError("여행 업데이트에 실패했습니다")

        return self._parse_trip_data(response.data[0])

    async def count_by_user_id(
        self,
        user_id: UUID,
        status: Optional[TripStatus] = None,
    ) -> int:
        """
        사용자의 여행 개수 조회
        """
        query = self.db.table("trips").select("id", count="exact").eq("user_id", str(user_id))

        if status is not None:
            query = query.eq("status", status.value)

        response = query.execute()
        return response.count or 0

    async def get_by_status(
        self,
        status: TripStatus,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Trip]:
        """
        특정 상태의 여행 목록 조회 (관리자용)
        최신순으로 정렬하여 반환
        """
        query = (
            self.db.table("trips")
            .select("*")
            .eq("status", status.value)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
        )
        response = query.execute()

        return [self._parse_trip_data(row) for row in response.data]

    async def count_by_status(self, status: TripStatus) -> int:
        """
        특정 상태의 여행 개수 조회 (관리자용)
        """
        query = self.db.table("trips").select("id", count="exact").eq("status", status.value)
        response = query.execute()
        return response.count or 0
