"""
Auth API Routes

인증/인가 관련 API 엔드포인트 정의
회원가입, 로그인, 프로필 조회/수정 기능 제공
"""

from fastapi import APIRouter, Depends, status

from src.api.dependencies.auth_deps import CurrentUser, get_auth_service
from src.api.schemas.auth_schemas import (
    LoginRequest,
    LoginResponse,
    SignupRequest,
    SignupResponse,
    UpdateProfileRequest,
    UserProfileResponse,
)
from src.application.services.auth_service import AuthService
from src.shared.schemas.response import SuccessResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=SuccessResponse[SignupResponse],
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="새로운 사용자 계정을 생성합니다. Supabase Auth와 users 테이블에 동시에 등록됩니다.",
)
async def signup(
    request: SignupRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    회원가입 엔드포인트
    이메일, 비밀번호, 사용자명을 받아 새 계정 생성
    """
    user, access_token = await auth_service.signup(
        email=request.email,
        password=request.password,
        username=request.username,
        vehicle_number=request.vehicle_number,
    )

    response_data = SignupResponse(
        user=UserProfileResponse.model_validate(user),
        access_token=access_token,
        token_type="bearer",
    )

    return SuccessResponse.create(
        message="회원가입이 완료되었습니다",
        data=response_data,
    )


@router.post(
    "/login",
    response_model=SuccessResponse[LoginResponse],
    status_code=status.HTTP_200_OK,
    summary="로그인",
    description="이메일과 비밀번호로 인증하여 JWT 토큰을 발급받습니다.",
)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    로그인 엔드포인트
    이메일과 비밀번호로 인증 후 JWT 토큰 반환
    """
    user, access_token = await auth_service.login(
        email=request.email,
        password=request.password,
    )

    response_data = LoginResponse(
        user=UserProfileResponse.model_validate(user),
        access_token=access_token,
        token_type="bearer",
    )

    return SuccessResponse.create(
        message="로그인에 성공했습니다",
        data=response_data,
    )


@router.get(
    "/profile",
    response_model=SuccessResponse[UserProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="프로필 조회",
    description="현재 로그인한 사용자의 프로필 정보를 조회합니다. (JWT 인증 필요)",
)
async def get_profile(current_user: CurrentUser):
    """
    프로필 조회 엔드포인트
    JWT 토큰에서 사용자 정보를 추출하여 반환
    """
    return SuccessResponse.create(
        message="프로필 조회 성공",
        data=UserProfileResponse.model_validate(current_user),
    )


@router.put(
    "/profile",
    response_model=SuccessResponse[UserProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="프로필 수정",
    description="현재 로그인한 사용자의 프로필 정보를 수정합니다. (JWT 인증 필요)",
)
@router.patch(
    "/profile",
    response_model=SuccessResponse[UserProfileResponse],
    status_code=status.HTTP_200_OK,
    summary="프로필 수정 (부분)",
    description="현재 로그인한 사용자의 프로필 정보를 부분 수정합니다. (JWT 인증 필요)",
)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: CurrentUser,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    프로필 수정 엔드포인트
    사용자명 또는 차량번호를 업데이트
    """
    updated_user = await auth_service.update_profile(
        user_id=current_user.id,
        username=request.username,
        vehicle_number=request.vehicle_number,
    )

    return SuccessResponse.create(
        message="프로필이 수정되었습니다",
        data=UserProfileResponse.model_validate(updated_user),
    )
