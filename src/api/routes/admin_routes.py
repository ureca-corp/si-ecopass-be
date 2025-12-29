"""
Admin API Routes

관리자 전용 API 엔드포인트 정의
여정 승인/반려, 역/주차장 CRUD 기능 제공
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies.admin_deps import AdminUser
from src.api.dependencies.admin_service_deps import get_admin_service
from src.api.dependencies.station_deps import get_station_service
from src.api.schemas.admin_schemas import (
    AdminTripDetailResponse,
    AdminTripListResponse,
    AdminTripResponse,
    AdminTripWithUserResponse,
    DashboardStatsResponse,
    UserInfoResponse,
)
from src.api.schemas.station_schemas import (
    AddressSearchResponse,
    CreateParkingLotRequest,
    CreateStationRequest,
    ParkingLotResponse,
    StationResponse,
    UpdateParkingLotRequest,
    UpdateStationRequest,
)
from src.application.services.admin_service import AdminService
from src.application.services.station_service import StationService
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
    각 여정에 사용자 정보 포함
    """
    # user_id 문자열을 UUID로 변환
    parsed_user_id = UUID(user_id) if user_id else None

    trips_with_users, total_count = await admin_service.get_all_trips(
        status=status,
        user_id=parsed_user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )

    # dict를 AdminTripWithUserResponse로 변환
    trip_responses = [AdminTripWithUserResponse(**trip) for trip in trips_with_users]
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
    각 여정에 사용자 정보 포함
    """
    trips_with_users, total_count = await admin_service.get_pending_trips(limit=limit, offset=offset)

    # dict를 AdminTripWithUserResponse로 변환
    trip_responses = [AdminTripWithUserResponse(**trip) for trip in trips_with_users]
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
    description="관리자 전용: 여정을 승인하고 포인트를 지급합니다. estimated_points가 earned_points로 지급됩니다. (관리자 권한 필수)",
)
async def approve_trip(
    trip_id: str,
    admin_user: AdminUser,
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    여정 승인 엔드포인트
    COMPLETED 상태의 여정을 APPROVED로 변경하고 사용자에게 포인트 지급
    estimated_points가 earned_points로 지급됨
    """
    trip = await admin_service.approve_trip(trip_id=UUID(trip_id))

    return SuccessResponse.create(
        message=f"여정이 승인되었습니다 (지급 포인트: {trip.earned_points}점)",
        data=AdminTripResponse.model_validate(trip),
    )


@router.post(
    "/trips/{trip_id}/reject",
    response_model=SuccessResponse[AdminTripResponse],
    status_code=status.HTTP_200_OK,
    summary="여정 반려",
    description="관리자 전용: 여정을 반려합니다. 포인트는 지급되지 않습니다. (관리자 권한 필수)",
)
async def reject_trip(
    trip_id: str,
    admin_user: AdminUser,
    admin_service: AdminService = Depends(get_admin_service),
):
    """
    여정 반려 엔드포인트
    COMPLETED 상태의 여정을 REJECTED로 변경
    포인트는 지급되지 않음
    """
    trip = await admin_service.reject_trip(trip_id=UUID(trip_id))

    return SuccessResponse.create(
        message="여정이 반려되었습니다",
        data=AdminTripResponse.model_validate(trip),
    )


# ============================================================================
# 역(Station) 관리 API
# ============================================================================


@router.post(
    "/stations",
    response_model=SuccessResponse[StationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="역 생성",
    description="관리자 전용: 새로운 지하철 역을 생성합니다.",
)
async def create_station(
    request: CreateStationRequest,
    admin_user: AdminUser,
    station_service: StationService = Depends(get_station_service),
):
    """새 역 생성"""
    station = await station_service.create_station(
        name=request.name,
        line_number=request.line_number,
        latitude=request.latitude,
        longitude=request.longitude,
    )
    return SuccessResponse.create(
        message=f"'{station.name}' 역이 생성되었습니다",
        data=StationResponse.model_validate(station),
    )


@router.put(
    "/stations/{station_id}",
    response_model=SuccessResponse[StationResponse],
    status_code=status.HTTP_200_OK,
    summary="역 수정",
    description="관리자 전용: 기존 역 정보를 수정합니다.",
)
async def update_station(
    station_id: UUID,
    request: UpdateStationRequest,
    admin_user: AdminUser,
    station_service: StationService = Depends(get_station_service),
):
    """역 정보 수정"""
    station = await station_service.update_station(
        station_id=station_id,
        name=request.name,
        line_number=request.line_number,
        latitude=request.latitude,
        longitude=request.longitude,
    )
    return SuccessResponse.create(
        message=f"'{station.name}' 역 정보가 수정되었습니다",
        data=StationResponse.model_validate(station),
    )


@router.delete(
    "/stations/{station_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="역 삭제",
    description="관리자 전용: 역을 삭제합니다. 연결된 주차장도 함께 삭제됩니다.",
)
async def delete_station(
    station_id: UUID,
    admin_user: AdminUser,
    station_service: StationService = Depends(get_station_service),
):
    """역 삭제 (연결된 주차장도 함께 삭제)"""
    await station_service.delete_station(station_id)
    return SuccessResponse.create(message="역이 삭제되었습니다", data=None)


# ============================================================================
# 주차장(Parking Lot) 관리 API
# ============================================================================


@router.post(
    "/parking-lots",
    response_model=SuccessResponse[ParkingLotResponse],
    status_code=status.HTTP_201_CREATED,
    summary="주차장 생성",
    description="관리자 전용: 새로운 주차장을 생성합니다. 주소만 입력하면 좌표와 거리가 자동 계산됩니다.",
)
async def create_parking_lot(
    request: CreateParkingLotRequest,
    admin_user: AdminUser,
    station_service: StationService = Depends(get_station_service),
):
    """
    새 주차장 생성 (자동 Geocoding + 거리 계산)

    어드민은 주소만 입력하면 백엔드에서 자동으로:
    1. 네이버 API로 주소 → 좌표 변환
    2. PostGIS로 역-주차장 거리 계산
    """
    parking_lot = await station_service.create_parking_lot(
        station_id=request.station_id,
        name=request.name,
        address=request.address,
        fee_info=request.fee_info,
    )
    return SuccessResponse.create(
        message=f"'{parking_lot.name}' 주차장이 생성되었습니다 (거리: {parking_lot.distance_to_station_m}m)",
        data=ParkingLotResponse.model_validate(parking_lot),
    )


@router.put(
    "/parking-lots/{parking_lot_id}",
    response_model=SuccessResponse[ParkingLotResponse],
    status_code=status.HTTP_200_OK,
    summary="주차장 수정",
    description="관리자 전용: 기존 주차장 정보를 수정합니다.",
)
async def update_parking_lot(
    parking_lot_id: UUID,
    request: UpdateParkingLotRequest,
    admin_user: AdminUser,
    station_service: StationService = Depends(get_station_service),
):
    """주차장 정보 수정"""
    parking_lot = await station_service.update_parking_lot(
        parking_lot_id=parking_lot_id,
        station_id=request.station_id,
        name=request.name,
        address=request.address,
        latitude=request.latitude,
        longitude=request.longitude,
        distance_to_station_m=request.distance_to_station_m,
        fee_info=request.fee_info,
    )
    return SuccessResponse.create(
        message=f"'{parking_lot.name}' 주차장 정보가 수정되었습니다",
        data=ParkingLotResponse.model_validate(parking_lot),
    )


@router.delete(
    "/parking-lots/{parking_lot_id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="주차장 삭제",
    description="관리자 전용: 주차장을 삭제합니다.",
)
async def delete_parking_lot(
    parking_lot_id: UUID,
    admin_user: AdminUser,
    station_service: StationService = Depends(get_station_service),
):
    """주차장 삭제"""
    await station_service.delete_parking_lot(parking_lot_id)
    return SuccessResponse.create(message="주차장이 삭제되었습니다", data=None)


# ============================================================================
# 주소 검색 API (네이버 Geocoding)
# ============================================================================


@router.get(
    "/address/search",
    response_model=SuccessResponse[AddressSearchResponse],
    status_code=status.HTTP_200_OK,
    summary="주소 검색 (자동완성)",
    description="관리자 전용: 네이버 Maps API로 주소를 검색합니다. 주차장 등록 시 정확한 주소 입력을 위해 사용.",
)
async def search_address(
    admin_user: AdminUser,
    query: str = Query(..., min_length=2, description="검색 키워드 (예: '대구 중구')"),
    limit: int = Query(10, ge=1, le=20, description="최대 결과 개수"),
):
    """
    주소 검색 API (자동완성용)

    프론트엔드에서 주소 입력 시 실시간으로 호출하여 자동완성 제공
    선택된 주소로 주차장 생성 요청
    """
    from src.config import get_settings
    from src.infrastructure.external.naver_geocoding_service import NaverGeocodingService

    settings = get_settings()

    geocoding_service = NaverGeocodingService(
        client_id=settings.naver_client_id,
        client_secret=settings.naver_client_secret,
    )

    results = await geocoding_service.search_addresses(query=query, limit=limit)

    return SuccessResponse.create(
        message=f"'{query}' 검색 완료 ({len(results)}건)",
        data=AddressSearchResponse(results=results, total_count=len(results)),
    )
