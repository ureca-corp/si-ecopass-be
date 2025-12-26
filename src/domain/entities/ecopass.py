"""
EcoPass Domain Entity

SQLModel 기반 도메인 엔티티 - DB 테이블과 Pydantic 모델을 통합
"""

from datetime import datetime, timezone
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


class EcoPass(SQLModel, table=True):
    """
    EcoPass 엔티티 (DB 테이블)

    환경 친화 활동 패스/인증서를 나타내는 핵심 도메인 모델
    """

    __tablename__ = "ecopasses"  # Supabase 테이블명

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="고유 식별자",
    )
    user_id: str = Field(
        index=True,
        description="패스 소유자 사용자 ID",
    )
    title: str = Field(
        min_length=1,
        max_length=200,
        description="패스 제목",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="패스 상세 설명",
    )
    points: int = Field(
        default=0,
        ge=0,
        description="획득한 환경 포인트",
    )
    is_active: bool = Field(
        default=True,
        description="패스 활성화 여부",
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True)),
        description="생성 시각",
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
                "user_id": "user_123",
                "title": "그린 출퇴근 패스",
                "description": "대중교통 이용 패스",
                "points": 100,
                "is_active": True,
            }
        }

    def add_points(self, points: int) -> None:
        """
        포인트 추가 (비즈니스 로직)
        음수 포인트는 허용하지 않음
        """
        if points < 0:
            raise ValueError("포인트는 양수여야 합니다")
        self.points += points
        self.updated_at = utc_now()

    def deactivate(self) -> None:
        """
        패스 비활성화
        updated_at 자동 갱신
        """
        self.is_active = False
        self.updated_at = utc_now()

    def activate(self) -> None:
        """
        패스 활성화
        updated_at 자동 갱신
        """
        self.is_active = True
        self.updated_at = utc_now()
