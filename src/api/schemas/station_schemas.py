"""
Station API Schemas

지하철 역 및 주차장 조회 API의 Request/Response 스키마 정의
"""

from typing import Optional
from uuid import UUID

from pydantic import Field

from src.infrastructure.external.naver_geocoding_service import AddressSearchResult
from src.shared.schemas.base import BaseRequest, BaseResponse


# ============================================================================
# Request Schemas (Admin용)
# ============================================================================


class CreateStationRequest(BaseRequest):
    """역 생성 요청 스키마"""

    name: str = Field(..., min_length=1, max_length=50, description="역 이름")
    line_number: int = Field(..., ge=1, le=4, description="노선 번호 (1=1호선, 2=2호선, 3=3호선, 4=대경선)")
    latitude: float = Field(..., ge=33, le=39, description="위도 (한국 남부 범위)")
    longitude: float = Field(..., ge=124, le=132, description="경도 (한국 범위)")


class UpdateStationRequest(BaseRequest):
    """역 수정 요청 스키마"""

    name: Optional[str] = Field(None, min_length=1, max_length=50, description="역 이름")
    line_number: Optional[int] = Field(None, ge=1, le=4, description="노선 번호")
    latitude: Optional[float] = Field(None, ge=33, le=39, description="위도")
    longitude: Optional[float] = Field(None, ge=124, le=132, description="경도")


class CreateParkingLotRequest(BaseRequest):
    """
    주차장 생성 요청 스키마 (간소화)

    어드민은 주소만 입력하면 백엔드에서 자동 처리:
    1. 네이버 Geocoding API로 주소 → 좌표 변환
    2. PostGIS로 역-주차장 거리 자동 계산
    """

    station_id: UUID = Field(..., description="연계 역 ID")
    name: str = Field(..., min_length=1, max_length=100, description="주차장 이름")
    address: str = Field(..., min_length=1, max_length=200, description="도로명 또는 지번 주소")
    fee_info: Optional[str] = Field(None, max_length=200, description="요금 정보")


class UpdateParkingLotRequest(BaseRequest):
    """주차장 수정 요청 스키마"""

    station_id: Optional[UUID] = Field(None, description="연계 역 ID")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="주차장 이름")
    address: Optional[str] = Field(None, min_length=1, max_length=200, description="주소")
    latitude: Optional[float] = Field(None, ge=33, le=39, description="위도")
    longitude: Optional[float] = Field(None, ge=124, le=132, description="경도")
    distance_to_station_m: Optional[int] = Field(None, ge=0, description="역까지 거리 (미터)")
    fee_info: Optional[str] = Field(None, max_length=200, description="요금 정보")


# ============================================================================
# Response Schemas
# ============================================================================


class StationResponse(BaseResponse):
    """
    개별 지하철 역 응답 스키마
    PostGIS 좌표가 latitude/longitude로 변환되어 제공됨
    """

    id: UUID
    name: str
    line_number: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "반월당역",
                "line_number": 1,
                "latitude": 35.8575,
                "longitude": 128.5974,
            }
        }


class ParkingLotResponse(BaseResponse):
    """
    주차장 응답 스키마
    역 주변 환승 주차장 정보
    """

    id: UUID
    station_id: UUID
    name: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_to_station_m: Optional[int] = None
    fee_info: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "650e8400-e29b-41d4-a716-446655440000",
                "station_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "반월당역 환승주차장",
                "address": "대구광역시 중구 동성로2가 123",
                "latitude": 35.8580,
                "longitude": 128.5980,
                "distance_to_station_m": 150,
                "fee_info": "1시간 1,000원, 추가 10분당 500원",
            }
        }


class StationListResponse(BaseResponse):
    """
    지하철 역 목록 응답 스키마
    리스트 형태로 여러 역 정보를 반환
    """

    stations: list[StationResponse]
    total_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "stations": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "반월당역",
                        "line_number": 1,
                        "latitude": 35.8575,
                        "longitude": 128.5974,
                    }
                ],
                "total_count": 14,
            }
        }


class StationDetailResponse(BaseResponse):
    """
    지하철 역 상세 정보 응답 스키마
    역 기본 정보 + 주변 주차장 목록 포함
    """

    id: UUID
    name: str
    line_number: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    parking_lots: list[ParkingLotResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "반월당역",
                "line_number": 1,
                "latitude": 35.8575,
                "longitude": 128.5974,
                "parking_lots": [
                    {
                        "id": "650e8400-e29b-41d4-a716-446655440000",
                        "station_id": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "반월당역 환승주차장",
                        "address": "대구광역시 중구 동성로2가 123",
                        "latitude": 35.8580,
                        "longitude": 128.5980,
                        "distance_to_station_m": 150,
                        "fee_info": "1시간 1,000원, 추가 10분당 500원",
                    }
                ],
            }
        }


class ParkingLotListResponse(BaseResponse):
    """
    주차장 목록 응답 스키마
    특정 역의 주차장 목록을 반환
    """

    parking_lots: list[ParkingLotResponse]
    total_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "parking_lots": [
                    {
                        "id": "650e8400-e29b-41d4-a716-446655440000",
                        "station_id": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "반월당역 환승주차장",
                        "address": "대구광역시 중구 동성로2가 123",
                        "latitude": 35.8580,
                        "longitude": 128.5980,
                        "distance_to_station_m": 150,
                        "fee_info": "1시간 1,000원, 추가 10분당 500원",
                    }
                ],
                "total_count": 9,
            }
        }


class AddressSearchResponse(BaseResponse):
    """
    주소 검색 결과 응답 스키마
    자동완성용 주소 리스트 반환
    """

    results: list[AddressSearchResult]
    total_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "address": "대구광역시 중구 동성로2가 123",
                        "jibun_address": "대구광역시 중구 동성로2가 123",
                        "latitude": 35.8580,
                        "longitude": 128.5980,
                    }
                ],
                "total_count": 5,
            }
        }
