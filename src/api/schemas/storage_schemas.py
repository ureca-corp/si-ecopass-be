"""
Storage API Schemas

이미지 업로드 관련 API 요청/응답 DTO (Data Transfer Objects)
모든 스키마는 ~~Request, ~~Response 명명 규칙을 따름
"""

from datetime import datetime

from pydantic import Field

from src.shared.schemas.base import BaseResponse


# ============================================================
# Response Schemas (응답 스키마)
# ============================================================


class ImageUploadResponse(BaseResponse):
    """
    이미지 업로드 응답 스키마
    업로드된 이미지의 URL과 메타데이터를 반환
    """

    image_url: str = Field(
        ...,
        description="업로드된 이미지의 공개 URL",
        examples=["https://supabase.co/storage/v1/object/public/trips/123e4567-e89b-12d3-a456-426614174000/transfer.jpg"],
    )
    uploaded_at: datetime = Field(
        ...,
        description="업로드 완료 시각 (UTC)",
    )
    stage: str = Field(
        ...,
        description="이미지 단계 (transfer 또는 arrival)",
        examples=["transfer", "arrival"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "image_url": "https://supabase.co/storage/v1/object/public/trips/123e4567-e89b-12d3-a456-426614174000/transfer.jpg",
                "uploaded_at": "2025-01-26T12:00:00Z",
                "stage": "transfer",
            }
        }
    }
