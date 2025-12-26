"""
Station API Routes

대구 지하철 역 및 주차장 조회 RESTful 엔드포인트
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies.station_deps import get_station_service
from src.api.schemas.station_schemas import (
    ParkingLotListResponse,
    ParkingLotResponse,
    StationDetailResponse,
    StationListResponse,
    StationResponse,
)
from src.application.services.station_service import StationService
from src.shared.schemas.response import SuccessResponse

router = APIRouter(prefix="/stations", tags=["Stations"])


@router.get(
    "",
    response_model=SuccessResponse[StationListResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all stations",
    description="Retrieve all subway stations, optionally filtered by line number",
)
async def get_all_stations(
    service: Annotated[StationService, Depends(get_station_service)],
    line_number: Annotated[
        Optional[int], Query(ge=1, le=3, description="Filter by line number (1, 2, 3)")
    ] = None,
):
    """
    지하철 역 목록 조회 (선택적 노선 필터링)

    - **line_number**: 노선 번호 (1, 2, 3) - 미지정 시 전체 조회
    """
    stations = await service.get_all_stations(line_number=line_number)

    return SuccessResponse.create(
        message=f"총 {len(stations)}개의 역을 조회했습니다"
        + (f" (노선 {line_number})" if line_number else ""),
        data=StationListResponse(
            stations=[StationResponse.model_validate(s) for s in stations],
            total_count=len(stations),
        ),
    )


@router.get(
    "/{station_id}",
    response_model=SuccessResponse[StationDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Get station details",
    description="Retrieve detailed information about a specific station including parking lots",
)
async def get_station_detail(
    station_id: UUID,
    service: Annotated[StationService, Depends(get_station_service)],
):
    """
    역 상세 정보 조회 (주차장 목록 포함)

    - **station_id**: 역 고유 식별자 (UUID)
    """
    # 역 기본 정보 조회
    station = await service.get_station_by_id(station_id)

    # 주차장 목록 조회
    parking_lots = await service.get_station_parking_lots(station_id)

    return SuccessResponse.create(
        message=f"{station.name} 상세 정보를 조회했습니다",
        data=StationDetailResponse(
            id=station.id,
            name=station.name,
            line_number=station.line_number,
            latitude=station.latitude,
            longitude=station.longitude,
            parking_lots=[ParkingLotResponse.model_validate(p) for p in parking_lots],
        ),
    )


@router.get(
    "/{station_id}/parking-lots",
    response_model=SuccessResponse[ParkingLotListResponse],
    status_code=status.HTTP_200_OK,
    summary="Get parking lots for a station",
    description="Retrieve all parking lots near a specific station",
)
async def get_station_parking_lots(
    station_id: UUID,
    service: Annotated[StationService, Depends(get_station_service)],
):
    """
    특정 역의 주차장 목록 조회

    - **station_id**: 역 고유 식별자 (UUID)
    """
    parking_lots = await service.get_station_parking_lots(station_id)

    return SuccessResponse.create(
        message=f"총 {len(parking_lots)}개의 주차장을 조회했습니다",
        data=ParkingLotListResponse(
            parking_lots=[ParkingLotResponse.model_validate(p) for p in parking_lots],
            total_count=len(parking_lots),
        ),
    )
