"""
Storage API Routes

이미지 업로드 관련 API 엔드포인트 정의
여행 인증 이미지 업로드 기능 제공
"""

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from src.api.dependencies.auth_deps import CurrentUser
from src.api.dependencies.storage_deps import get_storage_service
from src.api.schemas.storage_schemas import ImageUploadResponse
from src.application.services.storage_service import StorageService
from src.shared.schemas.response import SuccessResponse

router = APIRouter(prefix="/storage", tags=["Storage"])


@router.post(
    "/upload/transfer",
    response_model=SuccessResponse[ImageUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="환승 이미지 업로드",
    description="환승 인증 이미지를 업로드합니다. (JWT 인증 필요, multipart/form-data)",
)
async def upload_transfer_image(
    current_user: CurrentUser,
    file: UploadFile = File(..., description="업로드할 이미지 파일 (JPEG/PNG, 최대 5MB)"),
    storage_service: StorageService = Depends(get_storage_service),
):
    """
    환승 인증 이미지 업로드 엔드포인트
    환승 인증 이미지를 Supabase Storage에 업로드
    """
    # 이미지 업로드
    image_url = await storage_service.upload_image(
        user_id=current_user.id,
        image_file=file,
        stage="transfer",
    )

    # 응답 데이터 구성
    from datetime import datetime, timezone
    response_data = ImageUploadResponse(
        image_url=image_url,
        uploaded_at=datetime.now(timezone.utc),
        stage="transfer",
    )

    return SuccessResponse.create(
        message="환승 이미지가 업로드되었습니다",
        data=response_data,
    )


@router.post(
    "/upload/arrival",
    response_model=SuccessResponse[ImageUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="도착 이미지 업로드",
    description="도착 인증 이미지를 업로드합니다. (JWT 인증 필요, multipart/form-data)",
)
async def upload_arrival_image(
    current_user: CurrentUser,
    file: UploadFile = File(..., description="업로드할 이미지 파일 (JPEG/PNG, 최대 5MB)"),
    storage_service: StorageService = Depends(get_storage_service),
):
    """
    도착 인증 이미지 업로드 엔드포인트
    도착 인증 이미지를 Supabase Storage에 업로드
    """
    # 이미지 업로드
    image_url = await storage_service.upload_image(
        user_id=current_user.id,
        image_file=file,
        stage="arrival",
    )

    # 응답 데이터 구성
    from datetime import datetime, timezone
    response_data = ImageUploadResponse(
        image_url=image_url,
        uploaded_at=datetime.now(timezone.utc),
        stage="arrival",
    )

    return SuccessResponse.create(
        message="도착 이미지가 업로드되었습니다",
        data=response_data,
    )
