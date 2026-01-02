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
    JWT 토큰의 user_metadata에서 role을 읽어 'admin' 여부 확인
    users 테이블이 없어도 동작 (관리자는 user_metadata만으로 User 객체 생성)
    """
    token = credentials.credentials

    # Supabase Auth로 토큰 검증 및 관리자 여부 확인
    try:
        user_response = db.auth.get_user(token)
        if not user_response or not user_response.user:
            raise UnauthorizedError("유효하지 않은 토큰입니다")

        user_id = UUID(user_response.user.id)
        user_email = user_response.user.email

        # JWT 토큰의 user_metadata에서 role 추출
        user_metadata = user_response.user.user_metadata or {}
        role = user_metadata.get("role", "user")

        # JWT에서 바로 관리자 여부 확인
        if role != "admin":
            raise ForbiddenError("관리자 권한이 필요합니다")

        # users 테이블 조회 시도 (있으면 사용, 없으면 user_metadata로 생성)
        try:
            user = await auth_service.get_user_by_id(user_id)
            user.email = user_email
            user.role = role
            return user
        except Exception:
            # users 테이블에 없는 경우: user_metadata로 User 객체 생성
            user = User(
                id=user_id,
                email=user_email or "",
                username=user_metadata.get("username", "admin"),
                vehicle_number=None,
                role="admin",
                total_points=0,
            )
            return user

    except ForbiddenError:
        raise
    except UnauthorizedError:
        raise
    except Exception as e:
        raise UnauthorizedError(f"토큰 검증 실패: {str(e)}")


# 타입 힌트용 Annotated 별칭
AdminUser = Annotated[User, Depends(get_admin_user)]
