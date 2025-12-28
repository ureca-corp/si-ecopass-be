"""
Auth Dependencies

FastAPI 의존성 주입을 위한 인증/인가 관련 함수
JWT 토큰 검증 및 현재 사용자 조회 기능 제공
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client

from src.application.services.auth_service import AuthService
from src.domain.entities.user import User
from src.infrastructure.database.supabase import get_db
from src.shared.exceptions import UnauthorizedError

# HTTPBearer 스키마 정의 (Swagger UI Authorize 버튼 활성화)
security = HTTPBearer()


def get_auth_service(db: Client = Depends(get_db)) -> AuthService:
    """
    AuthService 의존성 주입
    FastAPI 엔드포인트에서 AuthService를 사용할 수 있도록 제공
    """
    return AuthService(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Client = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    JWT 토큰에서 현재 사용자 조회
    HTTPBearer를 통해 토큰을 추출하고 user_metadata에서 role 정보 읽기
    """
    token = credentials.credentials

    # Supabase Auth로 토큰 검증
    try:
        user_response = db.auth.get_user(token)
        if not user_response or not user_response.user:
            raise UnauthorizedError("유효하지 않은 토큰입니다")

        user_id = UUID(user_response.user.id)
        user_email = user_response.user.email

        # JWT 토큰의 user_metadata에서 role 추출 (DB 쿼리 불필요!)
        user_metadata = user_response.user.user_metadata or {}
        role = user_metadata.get("role", "user")

        # users 테이블에서 사용자 정보 조회
        user = await auth_service.get_user_by_id(user_id)

        # JWT에서 가져온 정보로 설정
        user.email = user_email
        user.role = role  # JWT의 role 사용 (성능 향상)
        return user

    except Exception as e:
        if isinstance(e, UnauthorizedError):
            raise
        raise UnauthorizedError(f"토큰 검증 실패: {str(e)}")


# 타입 힌트용 Annotated 별칭
CurrentUser = Annotated[User, Depends(get_current_user)]
