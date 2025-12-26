"""
pytest 픽스처 및 테스트 설정

모든 테스트에서 공통으로 사용하는 픽스처와 설정을 정의
"""

import os
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from supabase import Client, create_client

from src.config import Settings, get_settings
from src.main import app


# ============================================================
# 설정 픽스처
# ============================================================


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """
    테스트용 설정 인스턴스
    환경 변수에서 로드된 설정 반환
    """
    return get_settings()


# ============================================================
# FastAPI 클라이언트 픽스처
# ============================================================


@pytest.fixture(scope="function")
def test_client() -> Generator[TestClient, None, None]:
    """
    FastAPI TestClient 픽스처
    각 테스트마다 새로운 클라이언트 인스턴스 제공
    """
    with TestClient(app) as client:
        yield client


# ============================================================
# Supabase 클라이언트 픽스처
# ============================================================


@pytest.fixture(scope="session")
def supabase_client(test_settings: Settings) -> Client:
    """
    Supabase 클라이언트 픽스처
    테스트용 Supabase 인스턴스에 연결
    """
    return create_client(test_settings.supabase_url, test_settings.supabase_key)


# ============================================================
# 테스트 데이터 픽스처
# ============================================================


@pytest.fixture
def test_user_data() -> dict:
    """
    테스트용 일반 사용자 데이터
    회원가입/로그인 테스트에 사용
    """
    random_id = str(uuid4())[:8]
    return {
        "email": f"test_{random_id}@example.com",
        "password": "testpassword123",
        "username": f"테스트유저_{random_id}",
        "vehicle_number": "12가3456",
    }


@pytest.fixture
def admin_user_data() -> dict:
    """
    테스트용 관리자 사용자 데이터
    관리자 권한이 필요한 테스트에 사용
    참고: Supabase에서 수동으로 role='admin' 설정 필요
    """
    random_id = str(uuid4())[:8]
    return {
        "email": f"admin_{random_id}@example.com",
        "password": "adminpassword123",
        "username": f"관리자_{random_id}",
    }


@pytest.fixture
def test_trip_start_data() -> dict:
    """
    테스트용 여정 시작 데이터
    출발 위치 정보 (대구역 인근)
    """
    return {
        "latitude": 35.8809,  # 대구역 위도
        "longitude": 128.6286,  # 대구역 경도
    }


@pytest.fixture
def test_trip_transfer_data() -> dict:
    """
    테스트용 환승 데이터
    환승 위치 및 이미지 URL
    """
    return {
        "latitude": 35.8714,  # 중앙로역 위도
        "longitude": 128.5988,  # 중앙로역 경도
        "transfer_image_url": "https://example.com/transfer.jpg",
    }


@pytest.fixture
def test_trip_arrival_data() -> dict:
    """
    테스트용 도착 데이터
    도착 위치 및 이미지 URL
    """
    return {
        "latitude": 35.8569,  # 반월당역 위도
        "longitude": 128.5932,  # 반월당역 경도
        "arrival_image_url": "https://example.com/arrival.jpg",
    }


# ============================================================
# 인증된 클라이언트 픽스처
# ============================================================


@pytest.fixture
async def authenticated_client(test_client: TestClient, test_user_data: dict) -> TestClient:
    """
    인증된 일반 사용자 클라이언트 픽스처
    회원가입 후 JWT 토큰을 헤더에 추가한 클라이언트 반환
    """
    # 회원가입
    signup_response = test_client.post(
        "/api/v1/auth/signup",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
            "username": test_user_data["username"],
            "vehicle_number": test_user_data.get("vehicle_number"),
        },
    )

    if signup_response.status_code != 201:
        # 이미 존재하는 경우 로그인 시도
        login_response = test_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]},
        )
        access_token = login_response.json()["data"]["access_token"]
    else:
        access_token = signup_response.json()["data"]["access_token"]

    # 토큰을 헤더에 추가
    test_client.headers = {"Authorization": f"Bearer {access_token}"}
    return test_client


@pytest.fixture
async def admin_client(test_client: TestClient, admin_user_data: dict, supabase_client: Client) -> TestClient:
    """
    인증된 관리자 클라이언트 픽스처
    회원가입 후 관리자 권한 부여, JWT 토큰을 헤더에 추가한 클라이언트 반환

    주의: Supabase의 user_metadata에 role='admin' 설정 필요
    """
    # 회원가입
    signup_response = test_client.post(
        "/api/v1/auth/signup",
        json={
            "email": admin_user_data["email"],
            "password": admin_user_data["password"],
            "username": admin_user_data["username"],
        },
    )

    if signup_response.status_code != 201:
        # 이미 존재하는 경우 로그인 시도
        login_response = test_client.post(
            "/api/v1/auth/login",
            json={"email": admin_user_data["email"], "password": admin_user_data["password"]},
        )
        access_token = login_response.json()["data"]["access_token"]
        user_id = login_response.json()["data"]["user"]["id"]
    else:
        access_token = signup_response.json()["data"]["access_token"]
        user_id = signup_response.json()["data"]["user"]["id"]

    # Supabase에서 사용자를 관리자로 설정
    # 실제 환경에서는 Supabase Dashboard에서 수동 설정 필요
    try:
        supabase_client.table("users").update({"role": "admin"}).eq("id", user_id).execute()
    except Exception:
        pass  # 테스트 환경에서는 실패해도 계속 진행

    # 토큰을 헤더에 추가
    test_client.headers = {"Authorization": f"Bearer {access_token}"}
    return test_client


# ============================================================
# 데이터베이스 클린업 픽스처
# ============================================================


@pytest.fixture(autouse=True)
def cleanup_test_data(supabase_client: Client):
    """
    테스트 후 자동 데이터 정리
    테스트가 완료된 후 생성된 테스트 데이터를 삭제

    주의: 실제 프로덕션 환경에서는 사용하지 말 것!
    """
    yield  # 테스트 실행

    # 테스트 후 정리 로직 (필요한 경우 구현)
    # 예: 테스트용 사용자 삭제, 테스트용 여정 삭제 등
    pass


# ============================================================
# 환경 변수 확인
# ============================================================


@pytest.fixture(scope="session", autouse=True)
def check_test_environment():
    """
    테스트 환경 변수 확인
    필수 환경 변수가 설정되어 있는지 검증
    """
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        pytest.fail(f"필수 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")

    # 테스트 환경임을 명시
    print("\n" + "=" * 60)
    print("테스트 환경 시작")
    print("=" * 60 + "\n")

    yield

    print("\n" + "=" * 60)
    print("테스트 환경 종료")
    print("=" * 60 + "\n")
