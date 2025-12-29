"""
Trip Domain Entity

여행(이동) 엔티티 - 사용자의 차량 이동과 환승 정보를 관리
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """
    현재 UTC 시간을 timezone 정보와 함께 반환
    모든 timestamp 필드의 기본값으로 사용
    """
    return datetime.now(timezone.utc)


class TripStatus(str, Enum):
    """
    여행 상태 Enum
    상태 전이: DRIVING -> TRANSFERRED -> COMPLETED -> (APPROVED|REJECTED)
    """

    DRIVING = "DRIVING"  # 운전 중 (출발 후)
    TRANSFERRED = "TRANSFERRED"  # 환승 완료
    COMPLETED = "COMPLETED"  # 도착 완료 (포인트 계산 대기)
    APPROVED = "APPROVED"  # 관리자 승인 완료 (포인트 지급)
    REJECTED = "REJECTED"  # 관리자 거부 (포인트 미지급)


class Trip(SQLModel, table=True):
    """
    Trip 엔티티 (DB 테이블)

    사용자의 차량 이동 경로를 추적하고 환승 증빙 이미지를 관리하는 도메인 모델
    상태 머신을 통해 여행의 생명주기를 관리
    """

    __tablename__ = "trips"  # Supabase 테이블명

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="고유 식별자",
    )
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        description="사용자 ID (외래키)",
    )

    # 출발 정보
    start_latitude: float = Field(description="출발 위치 위도")
    start_longitude: float = Field(description="출발 위치 경도")

    # 환승 정보
    transfer_latitude: Optional[float] = Field(
        default=None,
        description="환승 위치 위도",
    )
    transfer_longitude: Optional[float] = Field(
        default=None,
        description="환승 위치 경도",
    )
    transfer_image_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="환승 증빙 이미지 URL",
    )

    # 도착 정보
    arrival_latitude: Optional[float] = Field(
        default=None,
        description="도착 위치 위도",
    )
    arrival_longitude: Optional[float] = Field(
        default=None,
        description="도착 위치 경도",
    )
    arrival_image_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="도착 증빙 이미지 URL",
    )

    # 상태 및 포인트
    status: TripStatus = Field(
        default=TripStatus.DRIVING,
        description="여행 상태",
    )
    points: Optional[int] = Field(
        default=None,
        ge=0,
        description="포인트 (도착 시 계산, 승인 시 지급)",
    )

    # 관리자 검토 정보
    admin_note: Optional[str] = Field(
        default=None,
        max_length=500,
        description="관리자 메모 (반려 사유 등)",
    )

    # 시간 정보
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
        description="레코드 생성 시각",
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
        description="최종 수정 시각",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "660e8400-e29b-41d4-a716-446655440001",
                "start_latitude": 37.5665,
                "start_longitude": 126.9780,
                "status": "DRIVING",
                "started_at": "2025-01-01T09:00:00Z",
            }
        }

    def can_transfer(self) -> bool:
        """
        환승 가능 여부 확인
        현재 상태가 DRIVING일 때만 환승 가능
        """
        return self.status == TripStatus.DRIVING

    def can_arrive(self) -> bool:
        """
        도착 기록 가능 여부 확인
        현재 상태가 TRANSFERRED일 때만 도착 가능
        """
        return self.status == TripStatus.TRANSFERRED

    def transfer(self, latitude: float, longitude: float, image_url: str) -> None:
        """
        환승 정보 기록 (비즈니스 로직)
        상태를 TRANSFERRED로 변경하고 환승 위치와 이미지 저장
        """
        if not self.can_transfer():
            raise ValueError(f"환승 불가능한 상태입니다: {self.status}")

        self.transfer_latitude = latitude
        self.transfer_longitude = longitude
        self.transfer_image_url = image_url
        self.status = TripStatus.TRANSFERRED
        self.updated_at = utc_now()

    def arrive(self, latitude: float, longitude: float, image_url: str, points: int) -> None:
        """
        도착 정보 기록 (비즈니스 로직)
        상태를 COMPLETED로 변경하고 도착 위치, 이미지, 포인트 저장
        """
        if not self.can_arrive():
            raise ValueError(f"도착 불가능한 상태입니다: {self.status}")

        self.arrival_latitude = latitude
        self.arrival_longitude = longitude
        self.arrival_image_url = image_url
        self.points = points
        self.status = TripStatus.COMPLETED
        self.updated_at = utc_now()

    def can_approve(self) -> bool:
        """
        승인 가능 여부 확인
        COMPLETED 상태일 때만 승인 가능
        """
        return self.status == TripStatus.COMPLETED

    def can_reject(self) -> bool:
        """
        반려 가능 여부 확인
        COMPLETED 상태일 때만 반려 가능
        """
        return self.status == TripStatus.COMPLETED

    def approve(self) -> None:
        """
        여정 승인 처리 (비즈니스 로직)
        상태를 APPROVED로 변경 (포인트는 그대로 유지)
        """
        if not self.can_approve():
            raise ValueError(f"현재 상태({self.status})에서는 승인할 수 없습니다")

        self.status = TripStatus.APPROVED
        self.updated_at = utc_now()

    def reject(self, admin_note: Optional[str] = None) -> None:
        """
        여정 반려 처리 (비즈니스 로직)
        상태를 REJECTED로 변경하고 반려 사유 기록
        """
        if not self.can_reject():
            raise ValueError(f"현재 상태({self.status})에서는 반려할 수 없습니다")

        self.status = TripStatus.REJECTED
        self.admin_note = admin_note
        self.updated_at = utc_now()
