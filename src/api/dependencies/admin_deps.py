"""
Admin Dependencies

관리자 권한 검증을 위한 FastAPI 의존성 주입 함수
Supabase Auth의 user_metadata.role을 확인하여 관리자 여부 판단
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from supabase import Client

from src.application.services.auth_service import AuthService
from src.domain.entities.user import User
from src.infrastructure.database.supabase import get_db
from src.shared.exceptions import ForbiddenError, UnauthorizedError

from .auth_deps import get_auth_service, security


async def get_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Client = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    관리자 권한 검증 후 현재 사용자 반환
    JWT 토큰의 user_metadata에서 role을 읽어 'admin' 여부 확인 (DB 쿼리 불필요)
    """
    token = credentials.credentials

    # Supabase Auth로 토큰 검증 및 관리자 여부 확인
    try:
        user_response = db.auth.get_user(token)
        if not user_response or not user_response.user:
            raise UnauthorizedError("유효하지 않은 토큰입니다")

        user_id = UUID(user_response.user.id)
        user_email = user_response.user.email

        # JWT 토큰의 user_metadata에서 role 추출 (성능 향상!)
        user_metadata = user_response.user.user_metadata or {}
        role = user_metadata.get("role", "user")

        # JWT에서 바로 관리자 여부 확인 (DB 쿼리 불필요)
        if role != "admin":
            raise ForbiddenError("관리자 권한이 필요합니다")

        # users 테이블에서 나머지 사용자 정보 조회
        user = await auth_service.get_user_by_id(user_id)

        # JWT에서 가져온 정보로 설정
        user.email = user_email
        user.role = role
        return user

    except ForbiddenError:
        raise
    except UnauthorizedError:
        raise
    except Exception as e:
        raise UnauthorizedError(f"토큰 검증 실패: {str(e)}")


# 타입 힌트용 Annotated 별칭
AdminUser = Annotated[User, Depends(get_admin_user)]
