"""
Trip API Routes

여행 관리 관련 API 엔드포인트 정의
여행 시작, 환승, 도착, 조회 기능 제공
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies.auth_deps import CurrentUser
from src.api.dependencies.trip_deps import get_trip_service
from src.api.schemas.trip_schemas import (
    ArrivalTripRequest,
    ArrivalTripResponse,
    StartTripRequest,
    StartTripResponse,
    TransferTripRequest,
    TransferTripResponse,
    TripListResponse,
    TripResponse,
)
from src.application.services.trip_service import TripService
from src.domain.entities.trip import TripStatus
from src.shared.schemas.response import SuccessResponse

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.post(
    "/start",
    response_model=SuccessResponse[StartTripResponse],
    status_code=status.HTTP_201_CREATED,
    summary="여행 시작",
    description="새로운 여행을 시작합니다. 출발 위치를 기록하고 상태를 DRIVING으로 설정합니다. (JWT 인증 필요)",
)
async def start_trip(
    request: StartTripRequest,
    current_user: CurrentUser,
    trip_service: TripService = Depends(get_trip_service),
):
    """
    여행 시작 엔드포인트
    출발 위치를 받아 새로운 여행 생성
    """
    trip = await trip_service.start_trip(
        user_id=current_user.id,
        latitude=request.latitude,
        longitude=request.longitude,
    )

    response_data = StartTripResponse(
        trip_id=trip.id,
        status=trip.status,
        started_at=trip.created_at,
    )

    return SuccessResponse.create(
        message="여행이 시작되었습니다",
        data=response_data,
    )


@router.post(
    "/{trip_id}/transfer",
    response_model=SuccessResponse[TransferTripResponse],
    status_code=status.HTTP_200_OK,
    summary="환승 기록",
    description="여행의 환승 정보를 기록합니다. 환승 위치와 증빙 이미지를 저장하고 상태를 TRANSFERRED로 변경합니다. (JWT 인증 필요)",
)
async def transfer_trip(
    trip_id: str,
    request: TransferTripRequest,
    current_user: CurrentUser,
    trip_service: TripService = Depends(get_trip_service),
):
    """
    환승 기록 엔드포인트
    환승 위치와 증빙 이미지를 받아 환승 정보 업데이트
    """
    from uuid import UUID

    trip = await trip_service.transfer_trip(
        trip_id=UUID(trip_id),
        user_id=current_user.id,
        latitude=request.latitude,
        longitude=request.longitude,
        image_url=str(request.transfer_image_url),
    )

    response_data = TransferTripResponse(
        trip_id=trip.id,
        status=trip.status,
        transferred_at=trip.updated_at,
    )

    return SuccessResponse.create(
        message="환승이 기록되었습니다",
        data=response_data,
    )


@router.post(
    "/{trip_id}/arrival",
    response_model=SuccessResponse[ArrivalTripResponse],
    status_code=status.HTTP_200_OK,
    summary="도착 기록",
    description="여행의 도착 정보를 기록합니다. 도착 위치와 증빙 이미지를 저장하고 상태를 COMPLETED로 변경하며 예상 포인트를 계산합니다. (JWT 인증 필요)",
)
async def arrive_trip(
    trip_id: str,
    request: ArrivalTripRequest,
    current_user: CurrentUser,
    trip_service: TripService = Depends(get_trip_service),
):
    """
    도착 기록 엔드포인트
    도착 위치와 증빙 이미지를 받아 도착 정보 업데이트
    """
    from uuid import UUID

    trip = await trip_service.arrive_trip(
        trip_id=UUID(trip_id),
        user_id=current_user.id,
        latitude=request.latitude,
        longitude=request.longitude,
        image_url=str(request.arrival_image_url),
    )

    response_data = ArrivalTripResponse(
        trip_id=trip.id,
        status=trip.status,
        arrived_at=trip.updated_at,
        estimated_points=trip.estimated_points,
    )

    return SuccessResponse.create(
        message="도착이 기록되었습니다",
        data=response_data,
    )


@router.get(
    "",
    response_model=SuccessResponse[TripListResponse],
    status_code=status.HTTP_200_OK,
    summary="여행 목록 조회",
    description="현재 사용자의 여행 목록을 조회합니다. 상태별 필터링 및 페이지네이션을 지원합니다. (JWT 인증 필요)",
)
async def get_trips(
    current_user: CurrentUser,
    trip_service: TripService = Depends(get_trip_service),
    status_filter: Optional[TripStatus] = Query(
        None,
        alias="status",
        description="필터링할 여행 상태",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="조회할 여행 개수 (최대 100개)",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="건너뛸 여행 개수 (페이지네이션)",
    ),
):
    """
    여행 목록 조회 엔드포인트
    사용자의 여행 목록을 상태별 필터링 및 페이지네이션하여 반환
    """
    trips = await trip_service.get_trips(
        user_id=current_user.id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )

    total_count = await trip_service.get_trip_count(
        user_id=current_user.id,
        status=status_filter,
    )

    trip_responses = [TripResponse.model_validate(trip) for trip in trips]
    response_data = TripListResponse(
        trips=trip_responses,
        total_count=total_count,
    )

    return SuccessResponse.create(
        message="여행 목록 조회 성공",
        data=response_data,
    )


@router.get(
    "/{trip_id}",
    response_model=SuccessResponse[TripResponse],
    status_code=status.HTTP_200_OK,
    summary="여행 상세 조회",
    description="특정 여행의 상세 정보를 조회합니다. (JWT 인증 필요)",
)
async def get_trip(
    trip_id: str,
    current_user: CurrentUser,
    trip_service: TripService = Depends(get_trip_service),
):
    """
    여행 상세 조회 엔드포인트
    특정 여행의 모든 정보를 반환
    """
    from uuid import UUID

    trip = await trip_service.get_trip_by_id(
        trip_id=UUID(trip_id),
        user_id=current_user.id,
    )

    return SuccessResponse.create(
        message="여행 조회 성공",
        data=TripResponse.model_validate(trip),
    )
