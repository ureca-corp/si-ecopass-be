"""
User Domain Entity

SQLModel 기반 사용자 엔티티 - Supabase Auth와 연동
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """
    현재 UTC 시간을 timezone 정보와 함께 반환
    모든 timestamp 필드의 기본값으로 사용
    """
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    """
    User 엔티티 (DB 테이블)

    Supabase Auth와 연동하여 사용자 정보를 관리하는 핵심 도메인 모델
    """

    __tablename__ = "users"  # Supabase 테이블명

    id: UUID = Field(
        primary_key=True,
        description="고유 식별자 (Supabase Auth의 user.id와 동일)",
    )
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="사용자 이메일 (로그인 계정)",
    )
    username: str = Field(
        max_length=100,
        description="사용자 닉네임",
    )
    vehicle_number: Optional[str] = Field(
        default=None,
        max_length=20,
        description="차량 번호 (선택 사항)",
    )
    role: str = Field(
        default="user",
        max_length=20,
        description="사용자 역할 (user, admin)",
    )
    total_points: int = Field(
        default=0,
        ge=0,
        description="누적 환경 포인트",
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
        description="계정 생성 시각",
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
        description="최종 수정 시각",
    )

    def is_admin(self) -> bool:
        """
        관리자 여부 확인
        role이 'admin'인 경우 True 반환
        """
        return self.role == "admin"

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "에코유저",
                "vehicle_number": "12가3456",
                "role": "user",
                "total_points": 500,
            }
        }

    def add_points(self, points: int) -> None:
        """
        포인트 추가 (비즈니스 로직)
        음수 포인트는 허용하지 않음
        """
        if points < 0:
            raise ValueError("포인트는 양수여야 합니다")
        self.total_points += points
        self.updated_at = utc_now()

    def update_profile(
        self,
        username: Optional[str] = None,
        vehicle_number: Optional[str] = None,
    ) -> None:
        """
        프로필 정보 업데이트
        변경된 필드만 업데이트하고 updated_at 갱신
        """
        if username is not None:
            self.username = username
        if vehicle_number is not None:
            self.vehicle_number = vehicle_number
        self.updated_at = utc_now()
