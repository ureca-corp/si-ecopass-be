"""
pytest 픽스처 및 테스트 설정

모든 테스트에서 공통으로 사용하는 픽스처와 설정을 정의
"""

import os
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from supabase import Client, create_client

# ============================================================
# 테스트 환경 변수 로드 (.env.test 우선)
# ============================================================
# 테스트 실행 시 .env.test를 먼저 로드하여 프로덕션 .env 오버라이드
if os.path.exists(".env.test"):
    load_dotenv(".env.test", override=True)
    print("✅ 테스트 환경 변수 로드: .env.test")
else:
    load_dotenv(".env")
    print("⚠️  .env.test 파일이 없어 .env 사용 (권장하지 않음)")

from src.config import Settings, get_settings
from src.infrastructure.database.session import init_db, close_db, get_session
from src.main import app

# get_settings() 캐시 클리어 (테스트 환경 변수 반영)
get_settings.cache_clear()


# ============================================================
# 설정 픽스처
# ============================================================


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """
    테스트용 설정 인스턴스
    .env.test에서 로드된 로컬 Supabase 설정 반환
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
# SQLModel Session 픽스처
# ============================================================


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    테스트 세션 시작 시 SQLModel Database Engine 초기화
    연결 실패 시 경고만 출력하고 계속 진행 (Supabase SDK 사용)
    """
    try:
        init_db()
        print("✅ SQLModel Database Engine initialized")
        yield
        close_db()
    except Exception as e:
        print(f"⚠️  SQLModel DB 연결 실패, Supabase SDK 사용: {str(e)[:100]}")
        yield


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    테스트용 SQLModel Session 픽스처
    각 테스트마다 새로운 세션 제공
    """
    session_gen = get_session()
    session = next(session_gen)
    yield session
    try:
        next(session_gen)
    except StopIteration:
        pass


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
        "points": 9,  # 예상 포인트 (총 거리 ~4577m ÷ 500 = 9포인트)
    }


# ============================================================
# 인증된 클라이언트 픽스처
# ============================================================


@pytest.fixture(scope="function")
def authenticated_client(test_client: TestClient, test_user_data: dict) -> Generator[TestClient, None, None]:
    """
    인증된 일반 사용자 클라이언트 픽스처
    회원가입 후 JWT 토큰을 헤더에 추가한 클라이언트 반환

    로컬 Supabase를 사용하므로 rate limit 없음
    """
    # 원본 헤더 백업 (테스트 후 복원용)
    original_headers = test_client.headers.copy() if test_client.headers else {}

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

    # 회원가입 성공 확인
    assert signup_response.status_code == 201, (
        f"Signup failed: {signup_response.status_code} - {signup_response.text}. "
        f"Email: {test_user_data['email']}"
    )

    response_data = signup_response.json()
    assert response_data is not None, "Signup response is None"
    assert "data" in response_data, f"No 'data' in response: {response_data}"
    access_token = response_data["data"]["access_token"]

    # 토큰을 헤더에 추가
    test_client.headers = {"Authorization": f"Bearer {access_token}"}

    yield test_client

    # 테스트 후 헤더 복원 (격리 보장)
    test_client.headers = original_headers


@pytest.fixture(scope="function")
def admin_client(test_client: TestClient, admin_user_data: dict, test_settings: Settings) -> Generator[TestClient, None, None]:
    """
    인증된 관리자 클라이언트 픽스처
    회원가입 후 관리자 권한 부여, JWT 토큰을 헤더에 추가한 클라이언트 반환

    로컬 Supabase를 사용하므로 rate limit 없음
    user_metadata에 role="admin" 설정 (service_role_key 사용)
    """
    # 원본 헤더 백업 (테스트 후 복원용)
    original_headers = test_client.headers.copy() if test_client.headers else {}

    # 회원가입
    signup_response = test_client.post(
        "/api/v1/auth/signup",
        json={
            "email": admin_user_data["email"],
            "password": admin_user_data["password"],
            "username": admin_user_data["username"],
        },
    )

    # 회원가입 성공 확인
    assert signup_response.status_code == 201, (
        f"Admin signup failed: {signup_response.status_code} - {signup_response.text}. "
        f"Email: {admin_user_data['email']}"
    )

    response_data = signup_response.json()
    assert response_data is not None, "Signup response is None"
    assert "data" in response_data, f"No 'data' in response: {response_data}"
    user_id = response_data["data"]["user"]["id"]

    # service_role_key로 Admin API 클라이언트 생성
    if test_settings.supabase_service_role_key:
        admin_supabase = create_client(
            test_settings.supabase_url,
            test_settings.supabase_service_role_key
        )

        # Supabase Admin API로 user_metadata 업데이트 (role="admin" 추가)
        try:
            admin_supabase.auth.admin.update_user_by_id(
                user_id,
                {"user_metadata": {"role": "admin"}}
            )
        except Exception as e:
            raise Exception(f"Failed to set admin role in user_metadata for user {user_id}: {e}")
    else:
        raise Exception("SUPABASE_SERVICE_ROLE_KEY not found in .env.test")

    # 새 토큰 발급을 위해 다시 로그인
    login_response = test_client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user_data["email"],
            "password": admin_user_data["password"],
        },
    )
    assert login_response.status_code == 200, f"Admin login failed: {login_response.text}"
    login_data = login_response.json()
    access_token = login_data["data"]["access_token"]

    # 토큰을 헤더에 추가
    test_client.headers = {"Authorization": f"Bearer {access_token}"}

    yield test_client

    # 테스트 후 헤더 복원 (격리 보장)
    test_client.headers = original_headers


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
    config.py에 기본값이 설정되어 있으므로 경고만 출력
    """
    settings = get_settings()

    # 테스트 환경임을 명시
    print("\n" + "=" * 60)
    print("테스트 환경 시작")
    print(f"Supabase URL: {settings.supabase_url}")
    print(f"Database URL: {settings.database_url[:50]}...")
    print("=" * 60 + "\n")

    yield

    print("\n" + "=" * 60)
    print("테스트 환경 종료")
    print("=" * 60 + "\n")
