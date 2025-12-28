"""
Admin API Routes

관리자 전용 API 엔드포인트 정의
여정 승인/반려 및 승인 대기 목록 조회 기능 제공
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies.admin_deps import AdminUser
from src.api.dependencies.admin_service_deps import get_admin_service
from src.api.schemas.admin_schemas import (
    AdminTripDetailResponse,
    AdminTripListResponse,
    AdminTripResponse,
    ApproveTripRequest,
    DashboardStatsResponse,
    RejectTripRequest,
    UserInfoResponse,
)
from src.application.services.admin_service import AdminService
from src.shared.schemas.response import SuccessResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/dashboard/stats",
    response_model=SuccessResponse[DashboardStatsResponse],
    status_code=status.HTTP_200_OK,
    summary="대시보드 통계 조회",
    description="관리자 전용: 전체 여정 통계를 상태별로 집계하여 반환합니다. (관리자 권한 필수)",
)
async def get_dashboard_stats(
    admin_user: AdminUser,
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    대시보드 통계 조회 엔드포인트
    전체 여정 수와 상태별 카운트를 반환
    """
    stats = await admin_service.get_dashboard_stats()

    return SuccessResponse.create(
        message="대시보드 통계 조회 성공",
        data=DashboardStatsResponse(**stats),
    )


@router.get(
    "/trips",
    response_model=SuccessResponse[AdminTripListResponse],
    status_code=status.HTTP_200_OK,
    summary="전체 여정 목록 조회",
    description="관리자 전용: 모든 여정 목록을 조회합니다. 상태, 사용자, 날짜 범위로 필터링 가능 (관리자 권한 필수)",
)
async def get_all_trips(
    admin_user: AdminUser,
    admin_service: AdminService = Depends(get_admin_service),
    status: str | None = Query(
        None,
        description="여정 상태 필터 (DRIVING, TRANSFERRED, COMPLETED, APPROVED, REJECTED)",
    ),
    user_id: str | None = Query(
        None,
        description="사용자 ID 필터 (특정 사용자의 여정만 조회)",
    ),
    start_date: str | None = Query(
        None,
        description="시작 날짜 필터 (ISO 8601 형식, 예: 2025-01-01T00:00:00Z)",
    ),
    end_date: str | None = Query(
        None,
        description="종료 날짜 필터 (ISO 8601 형식, 예: 2025-12-31T23:59:59Z)",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="조회할 여정 개수 (최대 100개)",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="건너뛸 여정 개수 (페이지네이션)",
    ),
):
    """
    전체 여정 목록 조회 엔드포인트
    상태, 사용자, 날짜 범위로 필터링 가능
    """
    # user_id 문자열을 UUID로 변환
    parsed_user_id = UUID(user_id) if user_id else None

    trips, total_count = await admin_service.get_all_trips(
        status=status,
        user_id=parsed_user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )

    trip_responses = [AdminTripResponse.model_validate(trip) for trip in trips]
    response_data = AdminTripListResponse(
        trips=trip_responses,
        total_count=total_count,
    )

    return SuccessResponse.create(
        message="여정 목록 조회 성공",
        data=response_data,
    )


@router.get(
    "/trips/pending",
    response_model=SuccessResponse[AdminTripListResponse],
    status_code=status.HTTP_200_OK,
    summary="승인 대기 여정 목록 조회",
    description="관리자 전용: COMPLETED 상태의 승인 대기 중인 여정 목록을 조회합니다. (관리자 권한 필수)",
)
async def get_pending_trips(
    admin_user: AdminUser,
    admin_service: AdminService = Depends(get_admin_service),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="조회할 여정 개수 (최대 100개)",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="건너뛸 여정 개수 (페이지네이션)",
    ),
):
    """
    승인 대기 여정 목록 조회 엔드포인트
    COMPLETED 상태의 여정들을 최신순으로 반환
    """
    trips, total_count = await admin_service.get_pending_trips(limit=limit, offset=offset)

    trip_responses = [AdminTripResponse.model_validate(trip) for trip in trips]
    response_data = AdminTripListResponse(
        trips=trip_responses,
        total_count=total_count,
    )

    return SuccessResponse.create(
        message="승인 대기 여정 목록 조회 성공",
        data=response_data,
    )


@router.get(
    "/trips/{trip_id}",
    response_model=SuccessResponse[AdminTripDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="여정 상세 조회",
    description="관리자 전용: 특정 여정의 상세 정보를 사용자 정보와 함께 조회합니다. (관리자 권한 필수)",
)
async def get_trip_detail(
    trip_id: str,
    admin_user: AdminUser,
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    여정 상세 조회 엔드포인트
    여정 정보와 사용자 정보를 함께 반환하여 관리자가 검토할 수 있도록 함
    """
    trip, user_info = await admin_service.get_trip_detail(UUID(trip_id))

    response_data = AdminTripDetailResponse(
        trip=AdminTripResponse.model_validate(trip),
        user=UserInfoResponse(**user_info),
    )

    return SuccessResponse.create(
        message="여정 상세 조회 성공",
        data=response_data,
    )


@router.post(
    "/trips/{trip_id}/approve",
    response_model=SuccessResponse[AdminTripResponse],
    status_code=status.HTTP_200_OK,
    summary="여정 승인",
    description="관리자 전용: 여정을 승인하고 포인트를 지급합니다. (관리자 권한 필수)",
)
async def approve_trip(
    trip_id: str,
    request: ApproveTripRequest,
    admin_user: AdminUser,
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    여정 승인 엔드포인트
    COMPLETED 상태의 여정을 APPROVED로 변경하고 사용자에게 포인트 지급
    earned_points 미입력 시 estimated_points 사용
    """
    trip = await admin_service.approve_trip(
        trip_id=UUID(trip_id),
        earned_points=request.earned_points,
    )

    return SuccessResponse.create(
        message=f"여정이 승인되었습니다 (지급 포인트: {trip.earned_points}점)",
        data=AdminTripResponse.model_validate(trip),
    )


@router.post(
    "/trips/{trip_id}/reject",
    response_model=SuccessResponse[AdminTripResponse],
    status_code=status.HTTP_200_OK,
    summary="여정 반려",
    description="관리자 전용: 여정을 반려하고 반려 사유를 기록합니다. (관리자 권한 필수)",
)
async def reject_trip(
    trip_id: str,
    request: RejectTripRequest,
    admin_user: AdminUser,
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    여정 반려 엔드포인트
    COMPLETED 상태의 여정을 REJECTED로 변경하고 반려 사유 기록
    포인트는 지급되지 않음
    """
    trip = await admin_service.reject_trip(
        trip_id=UUID(trip_id),
        admin_note=request.admin_note,
    )

    return SuccessResponse.create(
        message="여정이 반려되었습니다",
        data=AdminTripResponse.model_validate(trip),
    )
