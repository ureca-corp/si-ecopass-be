"""
Station API Schemas

지하철 역 및 주차장 조회 API의 Request/Response 스키마 정의
"""

from typing import Optional
from uuid import UUID

from src.shared.schemas.base import BaseResponse


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
