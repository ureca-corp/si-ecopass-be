"""
Trip Application Service

여행 관리 비즈니스 로직을 처리하는 애플리케이션 서비스
여행 시작, 환승, 도착 및 조회 유스케이스 구현
"""

from typing import Optional
from uuid import UUID

from src.domain.entities.trip import Trip, TripStatus
from src.domain.repositories.trip_repository import ITripRepository
from src.shared.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError


class TripService:
    """
    여행 서비스
    여행 생명주기 관리 및 상태 전이 비즈니스 규칙 적용
    """

    def __init__(self, trip_repository: ITripRepository):
        """
        TripService 초기화
        Trip 레포지토리를 의존성으로 주입받음
        """
        self.trip_repository = trip_repository

    async def start_trip(self, user_id: UUID, latitude: float, longitude: float) -> Trip:
        """
        여행 시작
        활성 여행이 있는지 확인 후 새로운 여행 생성
        """
        # 활성 여행이 있는지 확인
        active_trip = await self.trip_repository.get_active_trip(user_id)
        if active_trip:
            raise ConflictError(
                f"이미 진행 중인 여행이 있습니다 (ID: {active_trip.id}, 상태: {active_trip.status.value})"
            )

        # 새로운 여행 생성
        new_trip = Trip(
            user_id=user_id,
            start_latitude=latitude,
            start_longitude=longitude,
            status=TripStatus.DRIVING,
        )

        return await self.trip_repository.create(new_trip)

    async def transfer_trip(
        self,
        trip_id: UUID,
        user_id: UUID,
        latitude: float,
        longitude: float,
        image_url: str,
    ) -> Trip:
        """
        환승 기록
        소유권 확인 후 환승 정보 업데이트
        """
        # 여행 조회
        trip = await self.trip_repository.get_by_id(trip_id)
        if not trip:
            raise NotFoundError(f"여행을 찾을 수 없습니다 (ID: {trip_id})")

        # 소유권 확인
        if trip.user_id != user_id:
            raise ForbiddenError("다른 사용자의 여행을 수정할 수 없습니다")

        # 상태 확인 및 환승 기록
        try:
            trip.transfer(latitude=latitude, longitude=longitude, image_url=image_url)
        except ValueError as e:
            raise ValidationError(str(e))

        # 업데이트 저장
        return await self.trip_repository.update(trip)

    async def arrive_trip(
        self,
        trip_id: UUID,
        user_id: UUID,
        latitude: float,
        longitude: float,
        image_url: str,
        points: int,
    ) -> Trip:
        """
        도착 기록
        소유권 확인 후 도착 정보 업데이트 (포인트는 클라이언트에서 계산하여 전달)
        """
        # 여행 조회
        trip = await self.trip_repository.get_by_id(trip_id)
        if not trip:
            raise NotFoundError(f"여행을 찾을 수 없습니다 (ID: {trip_id})")

        # 소유권 확인
        if trip.user_id != user_id:
            raise ForbiddenError("다른 사용자의 여행을 수정할 수 없습니다")

        # 상태 확인 및 도착 기록
        try:
            trip.arrive(
                latitude=latitude,
                longitude=longitude,
                image_url=image_url,
                points=points,
            )
        except ValueError as e:
            raise ValidationError(str(e))

        # 업데이트 저장
        return await self.trip_repository.update(trip)

    async def get_trips(
        self,
        user_id: UUID,
        status: Optional[TripStatus] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Trip]:
        """
        사용자의 여행 목록 조회
        상태별 필터링 및 페이지네이션 지원
        """
        if limit < 1 or limit > 100:
            raise ValidationError("limit은 1에서 100 사이여야 합니다")

        if offset < 0:
            raise ValidationError("offset은 0 이상이어야 합니다")

        return await self.trip_repository.get_by_user_id(
            user_id=user_id,
            status=status,
            limit=limit,
            offset=offset,
        )

    async def get_trip_by_id(self, trip_id: UUID, user_id: UUID) -> Trip:
        """
        특정 여행 조회
        소유권 확인 후 반환
        """
        trip = await self.trip_repository.get_by_id(trip_id)
        if not trip:
            raise NotFoundError(f"여행을 찾을 수 없습니다 (ID: {trip_id})")

        # 소유권 확인
        if trip.user_id != user_id:
            raise ForbiddenError("다른 사용자의 여행을 조회할 수 없습니다")

        return trip

    async def get_trip_count(
        self,
        user_id: UUID,
        status: Optional[TripStatus] = None,
    ) -> int:
        """
        사용자의 여행 개수 조회
        상태별 필터링 지원
        """
        return await self.trip_repository.count_by_user_id(user_id=user_id, status=status)
