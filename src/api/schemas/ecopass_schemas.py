"""
EcoPass API Schemas

API 계층의 요청/응답 DTO (Data Transfer Objects)
모든 스키마는 ~~Request, ~~Response 명명 규칙을 따름
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from src.shared.schemas.base import BaseRequest, BaseResponse


# ============================================================
# Request Schemas (요청 스키마)
# ============================================================


class CreateEcoPassRequest(BaseRequest):
    """
    EcoPass 생성 요청 스키마
    새로운 환경 패스를 생성할 때 사용
    """

    user_id: str = Field(
        ...,
        min_length=1,
        description="사용자 ID",
        examples=["user_123"],
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="패스 제목",
        examples=["그린 출퇴근 패스"],
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="패스 상세 설명",
        examples=["대중교통 이용 패스"],
    )


class UpdateEcoPassRequest(BaseRequest):
    """
    EcoPass 수정 요청 스키마
    기존 패스의 정보를 업데이트할 때 사용
    """

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="패스 제목 (선택)",
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="패스 상세 설명 (선택)",
    )


class AddPointsRequest(BaseRequest):
    """
    포인트 추가 요청 스키마
    EcoPass에 포인트를 추가할 때 사용
    """

    points: int = Field(
        ...,
        gt=0,
        description="추가할 포인트 (양수만 가능)",
        examples=[50],
    )


# ============================================================
# Response Schemas (응답 스키마)
# ============================================================


class EcoPassResponse(BaseResponse):
    """
    EcoPass 단일 응답 스키마
    엔티티를 클라이언트에 반환할 때 사용
    """

    id: UUID = Field(..., description="고유 식별자")
    user_id: str = Field(..., description="패스 소유자 사용자 ID")
    title: str = Field(..., description="패스 제목")
    description: Optional[str] = Field(None, description="패스 상세 설명")
    points: int = Field(..., description="획득한 환경 포인트")
    is_active: bool = Field(..., description="패스 활성화 여부")
    created_at: datetime = Field(..., description="생성 시각")
    updated_at: datetime = Field(..., description="최종 수정 시각")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user_123",
                "title": "그린 출퇴근 패스",
                "description": "대중교통 이용 패스",
                "points": 100,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
            }
        }
    }


class EcoPassListResponse(BaseResponse):
    """
    EcoPass 리스트 응답 스키마
    여러 개의 패스를 반환할 때 사용
    """

    items: list[EcoPassResponse] = Field(..., description="패스 목록")
    total: int = Field(..., description="전체 패스 개수")
