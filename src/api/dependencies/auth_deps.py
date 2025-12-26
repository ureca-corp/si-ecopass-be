"""
Auth Dependencies

FastAPI 의존성 주입을 위한 인증/인가 관련 함수
JWT 토큰 검증 및 현재 사용자 조회 기능 제공
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from supabase import Client

from src.application.services.auth_service import AuthService
from src.domain.entities.user import User
from src.infrastructure.database.supabase import get_db
from src.shared.exceptions import UnauthorizedError


def get_auth_service(db: Client = Depends(get_db)) -> AuthService:
    """
    AuthService 의존성 주입
    FastAPI 엔드포인트에서 AuthService를 사용할 수 있도록 제공
    """
    return AuthService(db)


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: Client = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    JWT 토큰에서 현재 사용자 조회
    Authorization 헤더에서 Bearer 토큰을 추출하여 Supabase Auth로 검증
    """
    if not authorization:
        raise UnauthorizedError("인증 토큰이 필요합니다")

    # Bearer 토큰 추출
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError("올바르지 않은 인증 형식입니다 (Bearer 토큰 필요)")

    token = parts[1]

    # Supabase Auth로 토큰 검증
    try:
        user_response = db.auth.get_user(token)
        if not user_response or not user_response.user:
            raise UnauthorizedError("유효하지 않은 토큰입니다")

        user_id = UUID(user_response.user.id)
        user_email = user_response.user.email

        # users 테이블에서 사용자 정보 조회
        user = await auth_service.get_user_by_id(user_id)
        
        # auth.users에서 가져온 email 설정
        user.email = user_email
        return user

    except Exception as e:
        if isinstance(e, UnauthorizedError):
            raise
        raise UnauthorizedError(f"토큰 검증 실패: {str(e)}")


# 타입 힌트용 Annotated 별칭
CurrentUser = Annotated[User, Depends(get_current_user)]
