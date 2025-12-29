"""
Admin API Schemas

관리자 전용 API의 Request/Response 스키마
여정 승인/반려 관련 데이터 전송 객체 (DTO) 정의
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from src.domain.entities.trip import TripStatus
from src.shared.schemas.base import BaseResponse


class AdminTripResponse(BaseResponse):
    """
    관리자용 여정 상세 응답 스키마
    모든 여정 정보 포함 (일반 사용자보다 더 많은 정보)
    """

    id: UUID
    user_id: UUID

    # 출발 정보
    start_latitude: float
    start_longitude: float

    # 환승 정보
    transfer_latitude: Optional[float] = None
    transfer_longitude: Optional[float] = None
    transfer_image_url: Optional[str] = None

    # 도착 정보
    arrival_latitude: Optional[float] = None
    arrival_longitude: Optional[float] = None
    arrival_image_url: Optional[str] = None

    # 상태 및 포인트
    status: TripStatus
    estimated_points: Optional[int] = None
    earned_points: Optional[int] = None

    # 관리자 검토 정보
    admin_note: Optional[str] = None

    # 시간 정보
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "660e8400-e29b-41d4-a716-446655440001",
                "start_latitude": 37.5665,
                "start_longitude": 126.9780,
                "transfer_latitude": 37.5700,
                "transfer_longitude": 126.9800,
                "transfer_image_url": "https://storage.example.com/transfer_123.jpg",
                "arrival_latitude": 37.5750,
                "arrival_longitude": 126.9850,
                "arrival_image_url": "https://storage.example.com/arrival_123.jpg",
                "status": "COMPLETED",
                "estimated_points": 150,
                "earned_points": None,
                "admin_note": None,
                "created_at": "2025-01-01T09:00:00Z",
                "updated_at": "2025-01-01T09:30:00Z",
            }
        }


class AdminTripWithUserResponse(BaseResponse):
    """
    관리자용 여정 + 사용자 정보 응답 스키마
    목록 조회 시 사용자 정보를 함께 반환
    """

    id: UUID
    user_id: UUID

    # 사용자 정보
    user: Optional["UserInfoResponse"] = None

    # 출발 정보
    start_latitude: float
    start_longitude: float

    # 환승 정보
    transfer_latitude: Optional[float] = None
    transfer_longitude: Optional[float] = None
    transfer_image_url: Optional[str] = None

    # 도착 정보
    arrival_latitude: Optional[float] = None
    arrival_longitude: Optional[float] = None
    arrival_image_url: Optional[str] = None

    # 상태 및 포인트
    status: TripStatus
    estimated_points: Optional[int] = None
    earned_points: Optional[int] = None

    # 관리자 검토 정보
    admin_note: Optional[str] = None

    # 시간 정보
    created_at: datetime
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "660e8400-e29b-41d4-a716-446655440001",
                "user": {
                    "id": "660e8400-e29b-41d4-a716-446655440001",
                    "username": "에코유저",
                    "email": "user@example.com",
                    "vehicle_number": "12가3456",
                    "total_points": 500,
                },
                "start_latitude": 37.5665,
                "start_longitude": 126.9780,
                "status": "COMPLETED",
                "estimated_points": 150,
                "created_at": "2025-01-01T09:00:00Z",
                "updated_at": "2025-01-01T09:30:00Z",
            }
        }


class AdminTripListResponse(BaseResponse):
    """
    관리자용 여정 목록 응답 스키마
    페이지네이션 정보 포함, 각 여정에 사용자 정보 포함
    """

    trips: list[AdminTripWithUserResponse]
    total_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "trips": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "user_id": "660e8400-e29b-41d4-a716-446655440001",
                        "user": {
                            "id": "660e8400-e29b-41d4-a716-446655440001",
                            "username": "에코유저",
                            "email": "user@example.com",
                            "vehicle_number": "12가3456",
                            "total_points": 500,
                        },
                        "start_latitude": 37.5665,
                        "start_longitude": 126.9780,
                        "status": "COMPLETED",
                        "estimated_points": 150,
                        "created_at": "2025-01-01T09:00:00Z",
                        "updated_at": "2025-01-01T09:30:00Z",
                    }
                ],
                "total_count": 25,
            }
        }


class UserInfoResponse(BaseResponse):
    """
    여정 상세 조회 시 포함되는 사용자 정보
    """

    id: UUID
    username: str
    email: str
    vehicle_number: Optional[str] = None
    total_points: int

    class Config:
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "username": "에코유저",
                "email": "user@example.com",
                "vehicle_number": "12가3456",
                "total_points": 500,
            }
        }


class AdminTripDetailResponse(BaseResponse):
    """
    관리자용 여정 상세 응답 스키마
    사용자 정보 포함
    """

    trip: AdminTripResponse
    user: UserInfoResponse

    class Config:
        json_schema_extra = {
            "example": {
                "trip": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "user_id": "660e8400-e29b-41d4-a716-446655440001",
                    "start_latitude": 35.8665,
                    "start_longitude": 128.5780,
                    "transfer_latitude": 35.8700,
                    "transfer_longitude": 128.5800,
                    "transfer_image_url": "https://storage.example.com/transfer_123.jpg",
                    "arrival_latitude": 35.8750,
                    "arrival_longitude": 128.5850,
                    "arrival_image_url": "https://storage.example.com/arrival_123.jpg",
                    "status": "COMPLETED",
                    "estimated_points": 150,
                    "earned_points": None,
                    "admin_note": None,
                    "created_at": "2025-01-01T09:00:00Z",
                    "updated_at": "2025-01-01T09:30:00Z",
                },
                "user": {
                    "id": "660e8400-e29b-41d4-a716-446655440001",
                    "username": "에코유저",
                    "email": "user@example.com",
                    "vehicle_number": "12가3456",
                    "total_points": 500,
                },
            }
        }


class DashboardStatsResponse(BaseResponse):
    """
    관리자 대시보드 통계 응답 스키마
    가입자 수, 상태별 여정 개수 포함
    """

    total_users: int = Field(description="전체 가입자 수")
    total_trips: int = Field(description="전체 여정 수")
    pending_count: int = Field(description="승인 대기 중 (COMPLETED)")
    approved_count: int = Field(description="승인 완료 (APPROVED)")
    rejected_count: int = Field(description="반려 (REJECTED)")
    in_progress_count: int = Field(description="진행 중 (DRIVING + TRANSFERRED)")

    class Config:
        json_schema_extra = {
            "example": {
                "total_users": 42,
                "total_trips": 150,
                "pending_count": 12,
                "approved_count": 120,
                "rejected_count": 8,
                "in_progress_count": 10,
            }
        }
