"""
Trip API Schemas

여행 관리 관련 API 요청/응답 DTO (Data Transfer Objects)
모든 스키마는 ~~Request, ~~Response 명명 규칙을 따름
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field, field_validator

from src.domain.entities.trip import TripStatus
from src.shared.schemas.base import BaseRequest, BaseResponse


# ============================================================
# Request Schemas (요청 스키마)
# ============================================================


class StartTripRequest(BaseRequest):
    """
    여행 시작 요청 스키마
    출발 위치의 위도/경도를 받아 새로운 여행 시작
    """

    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="출발 위치 위도",
        examples=[37.5665],
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="출발 위치 경도",
        examples=[126.9780],
    )


class TransferTripRequest(BaseRequest):
    """
    환승 기록 요청 스키마
    환승 위치와 증빙 이미지를 받아 환승 정보 기록
    """

    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="환승 위치 위도",
        examples=[37.5172],
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="환승 위치 경도",
        examples=[127.0473],
    )
    transfer_image_url: str = Field(
        ...,
        description="환승 증빙 이미지 URL (Supabase Signed URL 지원)",
        examples=["https://storage.supabase.co/transfers/image.jpg"],
    )

    @field_validator("transfer_image_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """URL 형식 기본 검증 (https:// 시작)"""
        if not v.startswith("https://"):
            raise ValueError("URL은 https://로 시작해야 합니다")
        return v


class ArrivalTripRequest(BaseRequest):
    """
    도착 기록 요청 스키마
    도착 위치와 증빙 이미지를 받아 도착 정보 기록
    """

    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="도착 위치 위도",
        examples=[37.4979],
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="도착 위치 경도",
        examples=[127.0276],
    )
    arrival_image_url: str = Field(
        ...,
        description="도착 증빙 이미지 URL (Supabase Signed URL 지원)",
        examples=["https://storage.supabase.co/arrivals/image.jpg"],
    )
    points: int = Field(
        ...,
        ge=0,
        description="포인트 (클라이언트에서 계산, 500m당 1포인트 기준)",
        examples=[5],
    )

    @field_validator("arrival_image_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """URL 형식 기본 검증 (https:// 시작)"""
        if not v.startswith("https://"):
            raise ValueError("URL은 https://로 시작해야 합니다")
        return v


# ============================================================
# Response Schemas (응답 스키마)
# ============================================================


class StartTripResponse(BaseResponse):
    """
    여행 시작 응답 스키마
    생성된 여행 ID, 상태, 출발 시각 반환
    """

    trip_id: UUID = Field(..., description="생성된 여행 ID")
    status: TripStatus = Field(..., description="여행 상태")
    started_at: datetime = Field(..., description="여행 시작 시각")

    model_config = {
        "json_schema_extra": {
            "example": {
                "trip_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "DRIVING",
                "started_at": "2025-01-01T09:00:00Z",
            }
        }
    }


class TransferTripResponse(BaseResponse):
    """
    환승 기록 응답 스키마
    여행 ID, 상태, 환승 시각 반환
    """

    trip_id: UUID = Field(..., description="여행 ID")
    status: TripStatus = Field(..., description="여행 상태")
    transferred_at: datetime = Field(..., description="환승 시각")

    model_config = {
        "json_schema_extra": {
            "example": {
                "trip_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "TRANSFERRED",
                "transferred_at": "2025-01-01T09:30:00Z",
            }
        }
    }


class ArrivalTripResponse(BaseResponse):
    """
    도착 기록 응답 스키마
    여행 ID, 상태, 도착 시각, 포인트 반환
    """

    trip_id: UUID = Field(..., description="여행 ID")
    status: TripStatus = Field(..., description="여행 상태")
    arrived_at: datetime = Field(..., description="도착 시각")
    points: int = Field(..., description="포인트")

    model_config = {
        "json_schema_extra": {
            "example": {
                "trip_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "COMPLETED",
                "arrived_at": "2025-01-01T10:00:00Z",
                "points": 5,
            }
        }
    }


class TripResponse(BaseResponse):
    """
    여행 상세 정보 응답 스키마
    여행의 모든 정보를 클라이언트에 반환
    """

    id: UUID = Field(..., description="여행 ID")
    user_id: UUID = Field(..., description="사용자 ID")
    start_latitude: float = Field(..., description="출발 위치 위도")
    start_longitude: float = Field(..., description="출발 위치 경도")
    transfer_latitude: Optional[float] = Field(None, description="환승 위치 위도")
    transfer_longitude: Optional[float] = Field(None, description="환승 위치 경도")
    transfer_image_url: Optional[str] = Field(None, description="환승 증빙 이미지 URL")
    arrival_latitude: Optional[float] = Field(None, description="도착 위치 위도")
    arrival_longitude: Optional[float] = Field(None, description="도착 위치 경도")
    arrival_image_url: Optional[str] = Field(None, description="도착 증빙 이미지 URL")
    status: TripStatus = Field(..., description="여행 상태")
    points: Optional[int] = Field(None, description="포인트")
    created_at: datetime = Field(..., description="레코드 생성 시각")
    updated_at: datetime = Field(..., description="최종 수정 시각")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "660e8400-e29b-41d4-a716-446655440001",
                "start_latitude": 37.5665,
                "start_longitude": 126.9780,
                "transfer_latitude": 37.5172,
                "transfer_longitude": 127.0473,
                "transfer_image_url": "https://storage.supabase.co/transfers/image.jpg",
                "arrival_latitude": 37.4979,
                "arrival_longitude": 127.0276,
                "arrival_image_url": "https://storage.supabase.co/arrivals/image.jpg",
                "status": "COMPLETED",
                "points": 5,
                "created_at": "2025-01-01T09:00:00Z",
                "updated_at": "2025-01-01T10:00:00Z",
            }
        }
    }


class TripListResponse(BaseResponse):
    """
    여행 목록 응답 스키마
    여행 목록과 총 개수를 반환
    """

    trips: list[TripResponse] = Field(..., description="여행 목록")
    total_count: int = Field(..., description="전체 여행 개수")

    model_config = {
        "json_schema_extra": {
            "example": {
                "trips": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "user_id": "660e8400-e29b-41d4-a716-446655440001",
                        "start_latitude": 37.5665,
                        "start_longitude": 126.9780,
                        "status": "COMPLETED",
                        "points": 5,
                        "created_at": "2025-01-01T09:00:00Z",
                        "updated_at": "2025-01-01T10:00:00Z",
                    }
                ],
                "total_count": 1,
            }
        }
    }
