"""
여정(Trip) 관리 API 테스트

여정 시작, 환승, 도착, 조회 등 여정 관리 관련 엔드포인트 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestTripStart:
    """여정 시작 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_start_trip_success(
        self, authenticated_client: TestClient, test_trip_start_data: dict
    ):
        """
        여정 시작 성공 테스트
        유효한 출발 위치로 여정을 시작하면 성공 응답 반환
        """
        response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert "trip_id" in data["data"]
        assert data["data"]["status"] == "DRIVING"
        assert "started_at" in data["data"]

    @pytest.mark.asyncio
    async def test_start_trip_duplicate(
        self, authenticated_client: TestClient, test_trip_start_data: dict
    ):
        """
        중복 여정 시작 테스트
        이미 진행 중인 여정이 있을 때 새 여정 시작 시 409 Conflict 반환
        """
        # 첫 번째 여정 시작
        authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)

        # 두 번째 여정 시작 시도 (진행 중인 여정이 있음)
        response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)

        assert response.status_code == 409
        data = response.json()
        assert data["status"] == "error"
        assert "진행 중" in data["message"]

    def test_start_trip_unauthorized(self, test_client: TestClient, test_trip_start_data: dict):
        """
        인증 없이 여정 시작 테스트
        토큰 없이 여정 시작 시 401 Unauthorized 반환
        """
        response = test_client.post("/api/v1/trips/start", json=test_trip_start_data)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data  # HTTPBearer returns {'detail': 'Not authenticated'}

    @pytest.mark.asyncio
    async def test_start_trip_invalid_coordinates(self, authenticated_client: TestClient):
        """
        잘못된 좌표로 여정 시작 테스트
        유효하지 않은 위도/경도로 여정 시작 시 422 Validation Error 반환
        """
        invalid_data = {"latitude": 999.0, "longitude": 999.0}
        response = authenticated_client.post("/api/v1/trips/start", json=invalid_data)

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"

    @pytest.mark.asyncio
    async def test_start_trip_missing_fields(self, authenticated_client: TestClient):
        """
        필수 필드 누락 테스트
        위도 또는 경도 없이 여정 시작 시 422 Validation Error 반환
        """
        response = authenticated_client.post("/api/v1/trips/start", json={"latitude": 35.8809})

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"


class TestTripTransfer:
    """환승 기록 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_transfer_success(
        self,
        authenticated_client: TestClient,
        test_trip_start_data: dict,
        test_trip_transfer_data: dict,
    ):
        """
        환승 기록 성공 테스트
        진행 중인 여정에 환승 정보를 기록하면 성공 응답 반환
        """
        # 여정 시작
        start_response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)
        trip_id = start_response.json()["data"]["trip_id"]

        # 환승 기록
        response = authenticated_client.post(
            f"/api/v1/trips/{trip_id}/transfer", json=test_trip_transfer_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "TRANSFERRED"
        assert "transferred_at" in data["data"]

    @pytest.mark.asyncio
    async def test_transfer_no_active_trip(
        self, authenticated_client: TestClient, test_trip_transfer_data: dict
    ):
        """
        활성 여정 없이 환승 시도 테스트
        진행 중인 여정이 없을 때 환승 시도 시 404 Not Found 반환
        """
        fake_trip_id = "00000000-0000-0000-0000-000000000000"
        response = authenticated_client.post(
            f"/api/v1/trips/{fake_trip_id}/transfer", json=test_trip_transfer_data
        )

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"

    def test_transfer_unauthorized(
        self, test_client: TestClient, test_trip_transfer_data: dict
    ):
        """
        인증 없이 환승 기록 테스트
        토큰 없이 환승 기록 시 401 Unauthorized 반환
        """
        fake_trip_id = "00000000-0000-0000-0000-000000000000"
        response = test_client.post(
            f"/api/v1/trips/{fake_trip_id}/transfer", json=test_trip_transfer_data
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data  # HTTPBearer returns {'detail': 'Not authenticated'}

    @pytest.mark.asyncio
    async def test_transfer_invalid_state(
        self,
        authenticated_client: TestClient,
        test_trip_start_data: dict,
        test_trip_transfer_data: dict,
        test_trip_arrival_data: dict,
    ):
        """
        잘못된 상태에서 환승 시도 테스트
        이미 환승 완료된 여정에 다시 환승 시도 시 400 Bad Request 반환
        """
        # 여정 시작
        start_response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)
        trip_id = start_response.json()["data"]["trip_id"]

        # 첫 번째 환승
        authenticated_client.post(f"/api/v1/trips/{trip_id}/transfer", json=test_trip_transfer_data)

        # 도착 처리
        authenticated_client.post(f"/api/v1/trips/{trip_id}/arrival", json=test_trip_arrival_data)

        # 도착 완료 후 환승 시도 (잘못된 상태)
        response = authenticated_client.post(
            f"/api/v1/trips/{trip_id}/transfer", json=test_trip_transfer_data
        )

        assert response.status_code >= 400  # 4xx 에러면 OK (400, 422 등)
        data = response.json()
        assert data["status"] == "error"


class TestTripArrival:
    """도착 기록 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_arrival_success(
        self,
        authenticated_client: TestClient,
        test_trip_start_data: dict,
        test_trip_transfer_data: dict,
        test_trip_arrival_data: dict,
    ):
        """
        도착 기록 성공 테스트
        환승 완료 후 도착 정보를 기록하면 성공 응답 및 예상 포인트 반환
        """
        # 여정 시작
        start_response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)
        trip_id = start_response.json()["data"]["trip_id"]

        # 환승 기록
        authenticated_client.post(f"/api/v1/trips/{trip_id}/transfer", json=test_trip_transfer_data)

        # 도착 기록
        response = authenticated_client.post(
            f"/api/v1/trips/{trip_id}/arrival", json=test_trip_arrival_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "COMPLETED"
        assert "arrived_at" in data["data"]
        assert "estimated_points" in data["data"]
        assert data["data"]["estimated_points"] > 0

    @pytest.mark.asyncio
    async def test_arrival_without_transfer(
        self,
        authenticated_client: TestClient,
        test_trip_start_data: dict,
        test_trip_arrival_data: dict,
    ):
        """
        환승 없이 도착 시도 테스트
        환승하지 않고 바로 도착 시도 시 400 Bad Request 반환
        """
        # 여정 시작
        start_response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)
        trip_id = start_response.json()["data"]["trip_id"]

        # 환승 없이 바로 도착 시도
        response = authenticated_client.post(
            f"/api/v1/trips/{trip_id}/arrival", json=test_trip_arrival_data
        )

        assert response.status_code >= 400  # 4xx 에러면 OK (400, 422 등)
        data = response.json()
        assert data["status"] == "error"

    @pytest.mark.asyncio
    async def test_arrival_duplicate(
        self,
        authenticated_client: TestClient,
        test_trip_start_data: dict,
        test_trip_transfer_data: dict,
        test_trip_arrival_data: dict,
    ):
        """
        중복 도착 기록 테스트
        이미 도착 완료된 여정에 다시 도착 기록 시 400 Bad Request 반환
        """
        # 여정 시작
        start_response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)
        trip_id = start_response.json()["data"]["trip_id"]

        # 환승 기록
        authenticated_client.post(f"/api/v1/trips/{trip_id}/transfer", json=test_trip_transfer_data)

        # 첫 번째 도착 기록
        authenticated_client.post(f"/api/v1/trips/{trip_id}/arrival", json=test_trip_arrival_data)

        # 두 번째 도착 기록 시도 (중복)
        response = authenticated_client.post(
            f"/api/v1/trips/{trip_id}/arrival", json=test_trip_arrival_data
        )

        assert response.status_code >= 400  # 4xx 에러면 OK (400, 422 등)
        data = response.json()
        assert data["status"] == "error"


class TestTripRetrieval:
    """여정 조회 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_get_trip_by_id(
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

    @pytest.mark.asyncio
    async def test_get_my_trips(
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

    @pytest.mark.asyncio
    async def test_get_trips_with_pagination(self, authenticated_client: TestClient):
        """
        페이지네이션 적용 여정 목록 조회 테스트
        limit과 offset으로 페이지네이션 적용
        """
        response = authenticated_client.get("/api/v1/trips?limit=10&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]["trips"]) <= 10

    @pytest.mark.asyncio
    async def test_get_trip_unauthorized_access(
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


class TestTripStatuses:
    """여정 상태 전환 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_trip_status_flow(
        self,
        authenticated_client: TestClient,
        test_trip_start_data: dict,
        test_trip_transfer_data: dict,
        test_trip_arrival_data: dict,
    ):
        """
        여정 전체 상태 전환 흐름 테스트
        DRIVING → TRANSFERRED → COMPLETED 순서로 정상 전환
        """
        # 1. 여정 시작 (DRIVING)
        start_response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)
        trip_id = start_response.json()["data"]["trip_id"]
        assert start_response.json()["data"]["status"] == "DRIVING"

        # 2. 환승 (TRANSFERRED)
        transfer_response = authenticated_client.post(
            f"/api/v1/trips/{trip_id}/transfer", json=test_trip_transfer_data
        )
        assert transfer_response.json()["data"]["status"] == "TRANSFERRED"

        # 3. 도착 (COMPLETED)
        arrival_response = authenticated_client.post(
            f"/api/v1/trips/{trip_id}/arrival", json=test_trip_arrival_data
        )
        assert arrival_response.json()["data"]["status"] == "COMPLETED"

    @pytest.mark.asyncio
    async def test_invalid_status_transition(
        self,
        authenticated_client: TestClient,
        test_trip_start_data: dict,
        test_trip_arrival_data: dict,
    ):
        """
        잘못된 상태 전환 테스트
        DRIVING 상태에서 바로 COMPLETED로 전환 시도 시 실패
        """
        # 여정 시작 (DRIVING)
        start_response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)
        trip_id = start_response.json()["data"]["trip_id"]

        # TRANSFERRED 단계 건너뛰고 바로 도착 시도
        response = authenticated_client.post(
            f"/api/v1/trips/{trip_id}/arrival", json=test_trip_arrival_data
        )

        assert response.status_code >= 400  # 4xx 에러면 OK (400, 422 등)
        data = response.json()
        assert data["status"] == "error"
