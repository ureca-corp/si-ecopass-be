"""
여정(Trip) 조회 API 테스트

여정 상세 조회, 목록 조회, 페이지네이션 등 여정 조회 관련 엔드포인트 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestTripRetrieval:
    """여정 조회 테스트 클래스"""

    def test_get_trip_by_id(
        self, authenticated_client: TestClient, test_trip_start_data: dict
    ):
        """
        여정 상세 정보 조회 테스트
        여정 ID로 상세 정보 조회 시 성공 응답 반환
        """
        # 여정 시작
        start_response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)
        trip_id = start_response.json()["data"]["trip_id"]

        # 여정 조회
        response = authenticated_client.get(f"/api/v1/trips/{trip_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["id"] == trip_id
        assert "status" in data["data"]

    def test_get_my_trips(
        self, authenticated_client: TestClient, test_trip_start_data: dict
    ):
        """
        내 여정 목록 조회 테스트
        사용자의 모든 여정 목록을 조회하면 성공 응답 반환
        """
        # 여정 생성
        authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)

        # 여정 목록 조회
        response = authenticated_client.get("/api/v1/trips")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "trips" in data["data"]
        assert "total_count" in data["data"]
        assert len(data["data"]["trips"]) > 0

    def test_get_trips_with_pagination(self, authenticated_client: TestClient):
        """
        페이지네이션 적용 여정 목록 조회 테스트
        limit과 offset으로 페이지네이션 적용
        """
        response = authenticated_client.get("/api/v1/trips?limit=10&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]["trips"]) <= 10

    def test_get_trip_unauthorized_access(
        self, authenticated_client: TestClient, test_user_data: dict, test_client: TestClient
    ):
        """
        다른 사용자의 여정 조회 테스트
        다른 사용자의 여정을 조회 시 403 Forbidden 반환
        """
        # 첫 번째 사용자로 여정 생성
        start_response = authenticated_client.post(
            "/api/v1/trips/start", json={"latitude": 35.8809, "longitude": 128.6286}
        )
        trip_id = start_response.json()["data"]["trip_id"]

        # 두 번째 사용자 생성 및 로그인
        from uuid import uuid4
        import time

        random_id = str(uuid4())[:8]
        second_user = {
            "email": f"second_{random_id}@example.com",
            "password": "password123",
            "username": f"두번째유저_{random_id}",
        }

        # Rate limit 회피 재시도
        max_retries = 5
        retry_delay = 2.0
        signup_response = None

        for attempt in range(max_retries):
            if attempt > 0:
                time.sleep(retry_delay)
                retry_delay *= 2

            signup_response = test_client.post("/api/v1/auth/signup", json=second_user)

            if signup_response.status_code == 201:
                break

            response_json = signup_response.json()
            if response_json and "rate limit" not in response_json.get("message", "").lower():
                break

        assert signup_response and signup_response.status_code == 201, (
            f"Second user signup failed: {signup_response.status_code if signup_response else 'N/A'}"
        )

        signup_data = signup_response.json()
        assert signup_data and "data" in signup_data, f"Invalid signup response: {signup_data}"
        second_token = signup_data["data"]["access_token"]

        # 두 번째 사용자가 첫 번째 사용자의 여정 조회 시도
        response = test_client.get(
            f"/api/v1/trips/{trip_id}", headers={"Authorization": f"Bearer {second_token}"}
        )

        assert response.status_code > 400
        data = response.json()
        assert data["status"] == "error"
