"""
Auth API Schemas

인증/인가 관련 API 요청/응답 DTO (Data Transfer Objects)
모든 스키마는 ~~Request, ~~Response 명명 규칙을 따름
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field

from src.shared.schemas.base import BaseRequest, BaseResponse


# ============================================================
# Request Schemas (요청 스키마)
# ============================================================


class SignupRequest(BaseRequest):
    """
    회원가입 요청 스키마
    새로운 사용자 계정을 생성할 때 사용
    """

    email: EmailStr = Field(
        ...,
        description="사용자 이메일 (로그인 계정)",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="비밀번호 (최소 6자)",
        examples=["password123"],
    )
    username: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="사용자 닉네임",
        examples=["에코유저"],
    )
    vehicle_number: Optional[str] = Field(
        None,
        max_length=20,
        description="차량 번호 (선택 사항)",
        examples=["12가3456"],
    )


class LoginRequest(BaseRequest):
    """
    로그인 요청 스키마
    이메일과 비밀번호로 인증할 때 사용
    """

    email: EmailStr = Field(
        ...,
        description="사용자 이메일",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="비밀번호",
        examples=["password123"],
    )


class UpdateProfileRequest(BaseRequest):
    """
    프로필 수정 요청 스키마
    사용자 정보를 업데이트할 때 사용
    """

    username: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="사용자 닉네임 (선택)",
        examples=["새닉네임"],
    )
    vehicle_number: Optional[str] = Field(
        None,
        max_length=20,
        description="차량 번호 (선택)",
        examples=["34나5678"],
    )


# ============================================================
# Response Schemas (응답 스키마)
# ============================================================


class UserProfileResponse(BaseResponse):
    """
    사용자 프로필 응답 스키마
    사용자 정보를 클라이언트에 반환할 때 사용
    """

    id: UUID = Field(..., description="고유 식별자")
    email: str = Field(..., description="사용자 이메일")
    username: str = Field(..., description="사용자 닉네임")
    vehicle_number: Optional[str] = Field(None, description="차량 번호")
    total_points: int = Field(..., description="누적 환경 포인트")
    created_at: datetime = Field(..., description="계정 생성 시각")
    updated_at: datetime = Field(..., description="최종 수정 시각")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "에코유저",
                "vehicle_number": "12가3456",
                "total_points": 500,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
            }
        }
    }


class SignupResponse(BaseResponse):
    """
    회원가입 응답 스키마
    새로 생성된 사용자 정보와 JWT 토큰을 반환
    """

    user: UserProfileResponse = Field(..., description="생성된 사용자 정보")
    access_token: str = Field(..., description="JWT 액세스 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")

    model_config = {
        "json_schema_extra": {
            "example": {
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "username": "에코유저",
                    "vehicle_number": "12가3456",
                    "total_points": 0,
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                },
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    }


class LoginResponse(BaseResponse):
    """
    로그인 응답 스키마
    인증된 사용자 정보와 JWT 토큰을 반환
    """

    user: UserProfileResponse = Field(..., description="사용자 정보")
    access_token: str = Field(..., description="JWT 액세스 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")

    model_config = {
        "json_schema_extra": {
            "example": {
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "username": "에코유저",
                    "vehicle_number": "12가3456",
                    "total_points": 500,
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                },
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    }
