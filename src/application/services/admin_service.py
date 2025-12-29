"""
Admin Application Service

관리자 권한이 필요한 비즈니스 로직을 처리하는 애플리케이션 서비스
여정 승인/반려 및 승인 대기 여정 관리 기능 제공
"""

from typing import Optional
from uuid import UUID

from src.application.services.auth_service import AuthService
from src.domain.entities.trip import Trip, TripStatus
from src.domain.repositories.trip_repository import ITripRepository
from src.shared.exceptions import NotFoundError, ValidationError


class AdminService:
    """
    관리자 서비스
    여정 승인/반려 및 포인트 지급 등의 유스케이스 구현
    """

    def __init__(self, trip_repository: ITripRepository, auth_service: AuthService):
        """
        AdminService 초기화
        TripRepository와 AuthService를 의존성으로 주입받음
        """
        self.trip_repository = trip_repository
        self.auth_service = auth_service

    async def get_all_trips(
        self,
        status: Optional[str] = None,
        user_id: Optional[UUID] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        """
        전체 여정 목록 조회 (필터링 가능, 사용자 정보 포함)
        상태, 사용자, 날짜 범위로 필터링 지원
        각 여정에 사용자 정보를 포함하여 반환
        """
        trip_status = None
        if status:
            try:
                trip_status = TripStatus(status)
            except ValueError:
                # 잘못된 상태값이면 빈 목록 반환
                return [], 0

        # 필터링된 조회
        trips = await self.trip_repository.get_with_filters(
            status=trip_status,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
        total_count = await self.trip_repository.count_with_filters(
            status=trip_status,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )

        # 각 여정에 사용자 정보 추가
        trips_with_users = []
        for trip in trips:
            user_info = await self._get_user_info_safe(trip.user_id)
            trip_dict = trip.model_dump()
            trip_dict["user"] = user_info
            trips_with_users.append(trip_dict)

        return trips_with_users, total_count

    async def _get_user_info_safe(self, user_id: UUID) -> Optional[dict]:
        """
        사용자 정보 조회 (에러 발생 시 None 반환)
        목록 조회 시 일부 사용자 조회 실패가 전체 조회를 실패시키지 않도록 함
        """
        try:
            user = await self.auth_service.get_user_by_id(user_id)
            return {
                "id": user.id,
                "username": user.username,
                "vehicle_number": user.vehicle_number,
                "total_points": user.total_points,
            }
        except Exception:
            # 사용자 조회 실패 시 None 반환
            return None

    async def get_pending_trips(self, limit: int = 10, offset: int = 0) -> tuple[list[dict], int]:
        """
        승인 대기 중인 여정 목록 조회 (사용자 정보 포함)
        COMPLETED 상태의 여정들을 최신순으로 반환
        """
        # COMPLETED 상태의 여정 조회
        trips = await self.trip_repository.get_by_status(
            status=TripStatus.COMPLETED,
            limit=limit,
            offset=offset,
        )

        # 전체 개수 조회 (페이지네이션용)
        total_count = await self.trip_repository.count_by_status(TripStatus.COMPLETED)

        # 각 여정에 사용자 정보 추가
        trips_with_users = []
        for trip in trips:
            user_info = await self._get_user_info_safe(trip.user_id)
            trip_dict = trip.model_dump()
            trip_dict["user"] = user_info
            trips_with_users.append(trip_dict)

        return trips_with_users, total_count

    async def approve_trip(self, trip_id: UUID, earned_points: Optional[int] = None) -> Trip:
        """
        여정 승인 및 포인트 지급
        1. 여정 조회 및 승인 가능 여부 확인
        2. 여정 상태를 APPROVED로 변경
        3. 사용자에게 포인트 지급
        """
        # 여정 조회
        trip = await self.trip_repository.get_by_id(trip_id)
        if not trip:
            raise NotFoundError(f"여정을 찾을 수 없습니다 (ID: {trip_id})")

        # 승인 가능 여부 확인 (비즈니스 로직에서 검증)
        try:
            trip.approve(earned_points)
        except ValueError as e:
            raise ValidationError(str(e))

        # DB 업데이트
        updated_trip = await self.trip_repository.update(trip)

        # 사용자에게 포인트 지급
        if updated_trip.earned_points and updated_trip.earned_points > 0:
            try:
                await self.auth_service.add_points(
                    user_id=updated_trip.user_id,
                    points=updated_trip.earned_points,
                )
            except Exception as e:
                # 포인트 지급 실패 시 에러 로깅 (실제 환경에서는 로깅 필요)
                # 현재는 Supabase 트랜잭션 미지원으로 롤백 불가
                # 추후 에러 처리 및 복구 로직 추가 필요
                raise ValidationError(f"포인트 지급 실패: {str(e)}")

        return updated_trip

    async def reject_trip(self, trip_id: UUID, admin_note: str) -> Trip:
        """
        여정 반려 처리
        1. 여정 조회 및 반려 가능 여부 확인
        2. 여정 상태를 REJECTED로 변경하고 반려 사유 기록
        """
        # 여정 조회
        trip = await self.trip_repository.get_by_id(trip_id)
        if not trip:
            raise NotFoundError(f"여정을 찾을 수 없습니다 (ID: {trip_id})")

        # 반려 가능 여부 확인 (비즈니스 로직에서 검증)
        try:
            trip.reject(admin_note)
        except ValueError as e:
            raise ValidationError(str(e))

        # DB 업데이트
        updated_trip = await self.trip_repository.update(trip)

        return updated_trip

    async def get_trip_count_by_status(self, status: TripStatus) -> int:
        """
        특정 상태의 여정 개수 조회
        페이지네이션을 위한 헬퍼 메서드
        """
        return await self.trip_repository.count_by_status(status)

    async def get_trip_detail(self, trip_id: UUID) -> tuple[Trip, dict]:
        """
        여정 상세 조회 (사용자 정보 포함)
        관리자가 여정 검토 시 사용자 정보도 함께 제공
        """
        # 여정 조회
        trip = await self.trip_repository.get_by_id(trip_id)
        if not trip:
            raise NotFoundError(f"여정을 찾을 수 없습니다 (ID: {trip_id})")

        # 사용자 정보 조회
        user = await self.auth_service.get_user_by_id(trip.user_id)

        # 사용자 정보를 딕셔너리로 반환 (email 제외)
        user_info = {
            "id": user.id,
            "username": user.username,
            "vehicle_number": user.vehicle_number,
            "total_points": user.total_points,
        }

        return trip, user_info

    async def get_dashboard_stats(self) -> dict:
        """
        대시보드 통계 조회
        상태별 여정 개수를 집계하여 반환
        """
        # 전체 여정 수
        total_trips = await self.trip_repository.count_all()

        # 상태별 카운트
        pending_count = await self.trip_repository.count_by_status(TripStatus.COMPLETED)
        approved_count = await self.trip_repository.count_by_status(TripStatus.APPROVED)
        rejected_count = await self.trip_repository.count_by_status(TripStatus.REJECTED)

        # 진행 중 (DRIVING + TRANSFERRED)
        driving_count = await self.trip_repository.count_by_status(TripStatus.DRIVING)
        transferred_count = await self.trip_repository.count_by_status(TripStatus.TRANSFERRED)
        in_progress_count = driving_count + transferred_count

        return {
            "total_trips": total_trips,
            "pending_count": pending_count,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "in_progress_count": in_progress_count,
        }
