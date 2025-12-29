"""
ParkingLot API Routes

주차장 조회 RESTful 엔드포인트
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies.station_deps import get_station_service
from src.api.schemas.station_schemas import (
    ParkingLotListResponse,
    ParkingLotResponse,
)
from src.application.services.station_service import StationService
from src.shared.schemas.response import SuccessResponse

router = APIRouter(prefix="/parking-lots", tags=["ParkingLots"])


@router.get(
    "",
    response_model=SuccessResponse[ParkingLotListResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all parking lots",
    description="Retrieve all parking lots with optional pagination",
)
async def get_all_parking_lots(
    service: Annotated[StationService, Depends(get_station_service)],
    limit: Annotated[Optional[int], Query(ge=1, le=100, description="Number of results to return")] = None,
    offset: Annotated[Optional[int], Query(ge=0, description="Number of results to skip")] = None,
):
    """
    전체 주차장 목록 조회 (페이지네이션 지원)

    - **limit**: 반환할 결과 수 (최대 100)
    - **offset**: 건너뛸 결과 수
    """
    parking_lots = await service.get_all_parking_lots(limit=limit, offset=offset)

    return SuccessResponse.create(
        message=f"총 {len(parking_lots)}개의 주차장을 조회했습니다",
        data=ParkingLotListResponse(
            parking_lots=[ParkingLotResponse.model_validate(p) for p in parking_lots],
            total_count=len(parking_lots),
        ),
    )


@router.get(
    "/{parking_lot_id}",
    response_model=SuccessResponse[ParkingLotResponse],
    status_code=status.HTTP_200_OK,
    summary="Get parking lot details",
    description="Retrieve detailed information about a specific parking lot",
)
async def get_parking_lot_detail(
    parking_lot_id: UUID,
    service: Annotated[StationService, Depends(get_station_service)],
):
    """
    주차장 상세 정보 조회

    - **parking_lot_id**: 주차장 고유 식별자 (UUID)
    """
    parking_lot = await service.get_parking_lot_by_id(parking_lot_id)

    return SuccessResponse.create(
        message=f"'{parking_lot.name}' 주차장 정보를 조회했습니다",
        data=ParkingLotResponse.model_validate(parking_lot),
    )
