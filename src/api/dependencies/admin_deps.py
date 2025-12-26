"""
Admin Dependencies

관리자 권한 검증을 위한 FastAPI 의존성 주입 함수
Supabase Auth의 user_metadata.role을 확인하여 관리자 여부 판단
"""

from typing import Annotated

from fastapi import Depends, Header
from supabase import Client

from src.application.services.auth_service import AuthService
from src.domain.entities.user import User
from src.infrastructure.database.supabase import get_db
from src.shared.exceptions import ForbiddenError, UnauthorizedError

from .auth_deps import get_auth_service


async def get_admin_user(
    authorization: Annotated[str | None, Header()] = None,
    db: Client = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    관리자 권한 검증 후 현재 사용자 반환
    JWT 토큰에서 사용자를 추출하고 users 테이블의 role이 'admin'인지 확인
    """
    if not authorization:
        raise UnauthorizedError("인증 토큰이 필요합니다")

    # Bearer 토큰 추출
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError("올바르지 않은 인증 형식입니다 (Bearer 토큰 필요)")

    token = parts[1]

    # Supabase Auth로 토큰 검증 및 관리자 여부 확인
    try:
        user_response = db.auth.get_user(token)
        if not user_response or not user_response.user:
            raise UnauthorizedError("유효하지 않은 토큰입니다")

        # users 테이블에서 사용자 정보 조회 (role 포함)
        from uuid import UUID

        user_id = UUID(user_response.user.id)
        user = await auth_service.get_user_by_id(user_id)

        # 데이터베이스의 role 필드로 관리자 여부 확인
        if not user.is_admin():
            raise ForbiddenError("관리자 권한이 필요합니다")

        return user

    except ForbiddenError:
        raise
    except UnauthorizedError:
        raise
    except Exception as e:
        raise UnauthorizedError(f"토큰 검증 실패: {str(e)}")


# 타입 힌트용 Annotated 별칭
AdminUser = Annotated[User, Depends(get_admin_user)]
