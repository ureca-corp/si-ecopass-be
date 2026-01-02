"""
Auth Application Service

인증/인가 관련 비즈니스 로직을 처리하는 애플리케이션 서비스
Supabase Auth와 users 테이블을 조율하여 유스케이스 구현
"""

from typing import Optional
from uuid import UUID

from supabase import Client
from supabase_auth.errors import AuthApiError

from src.domain.entities.user import User
from src.shared.exceptions import (
    ConflictError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


class AuthService:
    """
    인증/인가 서비스
    회원가입, 로그인, 프로필 관리 등의 유스케이스 구현
    """

    def __init__(self, db: Client):
        """
        AuthService 초기화
        Supabase 클라이언트를 의존성으로 주입받음
        """
        self.db = db

    async def signup(
        self,
        email: str,
        password: str,
        username: str,
        vehicle_number: Optional[str] = None,
        role: str = "user",
    ) -> tuple[User, str]:
        """
        회원가입 처리
        1. Supabase Auth에 사용자 생성 (user_metadata에 role 포함)
        2. users 테이블에 추가 정보 저장
        """
        try:
            # Supabase Auth에 사용자 등록 (user_metadata로 role 포함)
            auth_response = self.db.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {
                        "data": {
                            "username": username,
                            "vehicle_number": vehicle_number,
                            "role": role,  # JWT 토큰에 포함됨
                        }
                    },
                }
            )

            if not auth_response.user:
                raise ValidationError("회원가입에 실패했습니다")

            user_id = auth_response.user.id
            access_token = auth_response.session.access_token if auth_response.session else ""

            # 트리거가 자동으로 users 레코드를 생성했으므로, username, vehicle_number, role을 업데이트
            update_data = {
                "username": username,
                "vehicle_number": vehicle_number,
                "role": role,  # DB에도 role 저장 (source of truth)
            }
            self.db.table("users").update(update_data).eq("id", user_id).execute()

            # User 객체 생성하여 반환
            user = User(
                id=UUID(user_id),
                email=email,
                username=username,
                vehicle_number=vehicle_number,
                role=role,
                total_points=0,
            )

            return user, access_token

        except AuthApiError as e:
            # Supabase Auth 에러 처리
            error_message = str(e)
            if "already registered" in error_message.lower() or "already exists" in error_message.lower():
                raise ConflictError(f"이미 등록된 이메일입니다: {email}")
            raise ValidationError(f"회원가입 실패: {error_message}")

    async def login(self, email: str, password: str) -> tuple[User, str]:
        """
        로그인 처리
        1. Supabase Auth로 인증
        2. users 테이블에서 일반 사용자 정보 조회
        3. 관리자는 Auth 메타데이터만으로 로그인 (users 테이블 불필요)
        """
        try:
            # Supabase Auth 로그인
            auth_response = self.db.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password,
                }
            )

            if not auth_response.user or not auth_response.session:
                raise UnauthorizedError("로그인에 실패했습니다")

            user_id = auth_response.user.id
            user_email = auth_response.user.email
            access_token = auth_response.session.access_token
            user_metadata = auth_response.user.user_metadata or {}

            # users 테이블에서 일반 사용자 정보 조회
            user_response = self.db.table("users").select("*").eq("id", user_id).execute()

            # 일반 사용자인 경우: users 테이블에 레코드가 있어야 함
            if user_response.data:
                user_data = user_response.data[0]
                user_data["email"] = user_email
                user = User(**user_data)
                return user, access_token

            # users 테이블에 없는 경우: 관리자인지 확인
            user_role = user_metadata.get("role", "user")
            if user_role == "admin":
                # 관리자는 Auth 메타데이터만으로 User 객체 생성
                user = User(
                    id=UUID(user_id),
                    email=user_email or "",
                    username=user_metadata.get("username", "admin"),
                    vehicle_number=None,
                    role="admin",
                    total_points=0,
                )
                return user, access_token

            # 일반 사용자인데 users 테이블에 없으면 에러
            raise NotFoundError(f"사용자 정보를 찾을 수 없습니다 (ID: {user_id})")

        except AuthApiError as e:
            # Supabase Auth 에러 처리
            error_message = str(e)
            if "invalid" in error_message.lower() or "credentials" in error_message.lower():
                raise UnauthorizedError("이메일 또는 비밀번호가 올바르지 않습니다")
            raise UnauthorizedError(f"로그인 실패: {error_message}")

    async def get_user_by_id(self, user_id: UUID) -> User:
        """
        ID로 사용자 조회
        JWT 토큰에서 추출한 user_id로 프로필 조회 시 사용
        PostgreSQL function을 사용하여 auth.users의 email을 함께 가져옴
        """
        # PostgreSQL function 호출 (auth.users JOIN)
        response = self.db.rpc("get_user_with_email", {"p_user_id": str(user_id)}).execute()

        if not response.data or len(response.data) == 0:
            raise NotFoundError(f"사용자를 찾을 수 없습니다 (ID: {user_id})")

        user_data = response.data[0]

        # email이 없으면 빈 문자열로 설정
        if "email" not in user_data or user_data["email"] is None:
            user_data["email"] = ""

        return User(**user_data)

    async def update_profile(
        self,
        user_id: UUID,
        username: Optional[str] = None,
        vehicle_number: Optional[str] = None,
    ) -> User:
        """
        사용자 프로필 업데이트
        변경된 필드만 업데이트하고 updated_at 자동 갱신
        """
        # 기존 사용자 조회
        user = await self.get_user_by_id(user_id)

        # 비즈니스 로직으로 프로필 업데이트
        user.update_profile(username=username, vehicle_number=vehicle_number)

        # DB 업데이트
        update_data = user.model_dump(mode="json", exclude={"id", "email", "created_at"})
        self.db.table("users").update(update_data).eq("id", str(user_id)).execute()

        # 업데이트된 사용자 정보 반환
        return await self.get_user_by_id(user_id)

    async def add_points(self, user_id: UUID, points: int) -> User:
        """
        사용자 포인트 추가
        여정 승인 시 관리자가 포인트를 지급할 때 사용
        """
        # 기존 사용자 조회
        user = await self.get_user_by_id(user_id)

        # 비즈니스 로직으로 포인트 추가 (음수 검증 포함)
        user.add_points(points)

        # DB 업데이트
        update_data = user.model_dump(mode="json", exclude={"id", "email", "created_at"})
        self.db.table("users").update(update_data).eq("id", str(user_id)).execute()

        # 업데이트된 사용자 정보 반환
        return await self.get_user_by_id(user_id)

    async def count_all_users(self) -> int:
        """
        전체 사용자 수 조회
        관리자 대시보드 통계용
        PostgreSQL function으로 RLS 우회
        """
        response = self.db.rpc("count_all_users").execute()
        return response.data if response.data else 0
