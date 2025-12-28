"""
인증(Authentication) API 테스트

회원가입, 로그인, 프로필 조회/수정 등 인증 관련 엔드포인트 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestSignup:
    """회원가입 테스트 클래스"""

    def test_signup_success(self, test_client: TestClient, test_user_data: dict):
        """
        정상 회원가입 테스트
        유효한 데이터로 회원가입 시 성공 응답 반환
        """
        response = test_client.post("/api/v1/auth/signup", json=test_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "user" in data["data"]
        assert "access_token" in data["data"]
        assert data["data"]["user"]["email"] == test_user_data["email"]
        assert data["data"]["user"]["username"] == test_user_data["username"]
        assert data["data"]["user"]["total_points"] == 0
        assert data["data"]["token_type"] == "bearer"

    def test_signup_duplicate_email(self, test_client: TestClient, test_user_data: dict):
        """
        중복 이메일 회원가입 테스트
        이미 존재하는 이메일로 회원가입 시 409 Conflict 반환
        """
        # 첫 번째 회원가입
        test_client.post("/api/v1/auth/signup", json=test_user_data)

        # 동일 이메일로 두 번째 회원가입 시도
        response = test_client.post("/api/v1/auth/signup", json=test_user_data)

        assert response.status_code == 409
        data = response.json()
        assert data["status"] == "error"
        assert "이미" in data["message"] or "등록" in data["message"]

    def test_signup_invalid_email(self, test_client: TestClient, test_user_data: dict):
        """
        잘못된 이메일 형식 회원가입 테스트
        유효하지 않은 이메일로 회원가입 시 422 Validation Error 반환
        """
        test_user_data["email"] = "invalid-email"
        response = test_client.post("/api/v1/auth/signup", json=test_user_data)

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"

    def test_signup_short_password(self, test_client: TestClient, test_user_data: dict):
        """
        짧은 비밀번호 회원가입 테스트
        6자 미만의 비밀번호로 회원가입 시 422 Validation Error 반환
        """
        test_user_data["password"] = "12345"  # 5자
        response = test_client.post("/api/v1/auth/signup", json=test_user_data)

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"

    def test_signup_missing_required_fields(self, test_client: TestClient):
        """
        필수 필드 누락 테스트
        필수 필드 없이 회원가입 시 422 Validation Error 반환
        """
        response = test_client.post("/api/v1/auth/signup", json={"email": "test@example.com"})

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"


class TestLogin:
    """로그인 테스트 클래스"""

    def test_login_success(self, test_client: TestClient, test_user_data: dict):
        """
        정상 로그인 테스트
        유효한 이메일/비밀번호로 로그인 시 성공 응답 및 JWT 토큰 반환
        """
        # 회원가입
        test_client.post("/api/v1/auth/signup", json=test_user_data)

        # 로그인
        response = test_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "user" in data["data"]
        assert "access_token" in data["data"]
        assert data["data"]["user"]["email"] == test_user_data["email"]
        assert data["data"]["token_type"] == "bearer"

    def test_login_wrong_password(self, test_client: TestClient, test_user_data: dict):
        """
        잘못된 비밀번호 로그인 테스트
        틀린 비밀번호로 로그인 시 401 Unauthorized 반환
        """
        # 회원가입
        test_client.post("/api/v1/auth/signup", json=test_user_data)

        # 잘못된 비밀번호로 로그인 시도
        response = test_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": "wrongpassword"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["status"] == "error"

    def test_login_nonexistent_user(self, test_client: TestClient):
        """
        존재하지 않는 사용자 로그인 테스트
        등록되지 않은 이메일로 로그인 시 401 Unauthorized 반환
        """
        response = test_client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["status"] == "error"


class TestProfile:
    """프로필 관리 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_get_profile_success(self, authenticated_client: TestClient, test_user_data: dict):
        """
        프로필 조회 테스트
        인증된 사용자가 자신의 프로필을 조회하면 성공 응답 반환
        """
        response = authenticated_client.get("/api/v1/auth/profile")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["email"] == test_user_data["email"]
        assert data["data"]["username"] == test_user_data["username"]

    def test_get_profile_unauthorized(self, test_client: TestClient):
        """
        인증 없이 프로필 조회 테스트
        토큰 없이 프로필 조회 시 401 Unauthorized 반환
        """
        response = test_client.get("/api/v1/auth/profile")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data  # HTTPBearer returns {'detail': 'Not authenticated'}

    @pytest.mark.asyncio
    async def test_update_profile_success(self, authenticated_client: TestClient):
        """
        프로필 수정 테스트
        인증된 사용자가 프로필을 수정하면 성공 응답 반환
        """
        from uuid import uuid4
        unique_username = f"새닉네임_{str(uuid4())[:8]}"
        update_data = {"username": unique_username, "vehicle_number": "56나7890"}
        response = authenticated_client.put("/api/v1/auth/profile", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["username"] == unique_username
        assert data["data"]["vehicle_number"] == "56나7890"

    @pytest.mark.asyncio
    async def test_update_profile_partial(self, authenticated_client: TestClient):
        """
        부분 프로필 수정 테스트
        일부 필드만 수정 시 해당 필드만 업데이트됨
        """
        from uuid import uuid4
        unique_username = f"부분수정닉네임_{str(uuid4())[:8]}"
        update_data = {"username": unique_username}
        response = authenticated_client.put("/api/v1/auth/profile", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["username"] == unique_username

    def test_update_profile_unauthorized(self, test_client: TestClient):
        """
        인증 없이 프로필 수정 테스트
        토큰 없이 프로필 수정 시 401 Unauthorized 반환
        """
        update_data = {"username": "새닉네임"}
        response = test_client.put("/api/v1/auth/profile", json=update_data)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data  # HTTPBearer returns {'detail': 'Not authenticated'}
