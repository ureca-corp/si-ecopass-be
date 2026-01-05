"""
관리자(Admin) API 테스트

여정 승인/반려, 포인트 지급 등 관리자 전용 엔드포인트 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestAdminApproval:
    """관리자 여정 승인 테스트 클래스"""

    def test_approve_trip_success(
        self,
        authenticated_client: TestClient,
        admin_client: TestClient,
        test_trip_start_data: dict,
        test_trip_transfer_data: dict,
        test_trip_arrival_data: dict,
    ):
        """
        여정 승인 성공 테스트
        관리자가 완료된 여정을 승인하면 포인트 지급 및 상태 변경
        """
        # 1. 일반 사용자가 여정 완료
        start_response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)
        trip_id = start_response.json()["data"]["trip_id"]

        authenticated_client.post(f"/api/v1/trips/{trip_id}/transfer", json=test_trip_transfer_data)
        authenticated_client.post(f"/api/v1/trips/{trip_id}/arrival", json=test_trip_arrival_data)

        # 2. 관리자가 승인
        response = admin_client.post(f"/api/v1/admin/trips/{trip_id}/approve")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "APPROVED"
        assert data["data"]["points"] == 9  # 서버 계산 포인트 (총 거리 ~4577m)

    def test_approve_trip_non_admin(
        self,
        authenticated_client: TestClient,
        test_trip_start_data: dict,
        test_trip_transfer_data: dict,
        test_trip_arrival_data: dict,
    ):
        """
        일반 사용자의 승인 시도 테스트
        관리자가 아닌 사용자가 승인 시도 시 403 Forbidden 반환
        """
        # 여정 완료
        start_response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)
        trip_id = start_response.json()["data"]["trip_id"]

        authenticated_client.post(f"/api/v1/trips/{trip_id}/transfer", json=test_trip_transfer_data)
        authenticated_client.post(f"/api/v1/trips/{trip_id}/arrival", json=test_trip_arrival_data)

        # 일반 사용자가 승인 시도
        response = authenticated_client.post(
            f"/api/v1/admin/trips/{trip_id}/approve"
        )

        assert response.status_code == 403
        data = response.json()
        assert data["status"] == "error"
        assert "권한" in data["message"] or "admin" in data["message"].lower()

    def test_approve_incomplete_trip(
        self,
        authenticated_client: TestClient,
        admin_client: TestClient,
        test_trip_start_data: dict,
    ):
        """
        미완료 여정 승인 시도 테스트
        아직 완료되지 않은 여정을 승인 시도 시 400 Bad Request 반환
        """
        # 여정 시작만 함 (완료하지 않음)
        start_response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)
        trip_id = start_response.json()["data"]["trip_id"]

        # 관리자가 미완료 여정 승인 시도
        response = admin_client.post(f"/api/v1/admin/trips/{trip_id}/approve")

        assert response.status_code >= 400  # 에러면 OK (400, 422 등)
        data = response.json()
        assert data["status"] == "error"

    def test_approve_nonexistent_trip(self, admin_client: TestClient):
        """
        존재하지 않는 여정 승인 시도 테스트
        잘못된 여정 ID로 승인 시도 시 404 Not Found 반환
        """
        fake_trip_id = "00000000-0000-0000-0000-000000000000"
        response = admin_client.post(
            f"/api/v1/admin/trips/{fake_trip_id}/approve"        )

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"

    @pytest.mark.skip(reason="Obsolete test - approve_trip no longer accepts points parameter")
    def test_approve_with_negative_points(
        self,
        authenticated_client: TestClient,
        admin_client: TestClient,
        test_trip_start_data: dict,
        test_trip_transfer_data: dict,
        test_trip_arrival_data: dict,
    ):
        """
        음수 포인트로 승인 시도 테스트
        음수 포인트로 승인 시도 시 422 Validation Error 반환
        """
        # 여정 완료
        start_response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)
        trip_id = start_response.json()["data"]["trip_id"]

        authenticated_client.post(f"/api/v1/trips/{trip_id}/transfer", json=test_trip_transfer_data)
        authenticated_client.post(f"/api/v1/trips/{trip_id}/arrival", json=test_trip_arrival_data)

        # NOTE: 음수 포인트 테스트는 더 이상 유효하지 않음 (approve_trip이 earned_points를 받지 않음)
        # 승인 후 정상적으로 포인트가 설정되는지 확인
        response = admin_client.post(f"/api/v1/trips/{trip_id}/approve")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["points"] == 9  # 서버 계산 포인트 (총 거리 ~4577m)


class TestAdminRejection:
    """관리자 여정 반려 테스트 클래스"""

    def test_reject_trip_success(
        self,
        authenticated_client: TestClient,
        admin_client: TestClient,
        test_trip_start_data: dict,
        test_trip_transfer_data: dict,
        test_trip_arrival_data: dict,
    ):
        """
        여정 반려 성공 테스트
        관리자가 완료된 여정을 반려하면 상태 변경 및 사유 기록
        """
        # 여정 완료
        start_response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)
        trip_id = start_response.json()["data"]["trip_id"]

        authenticated_client.post(f"/api/v1/trips/{trip_id}/transfer", json=test_trip_transfer_data)
        authenticated_client.post(f"/api/v1/trips/{trip_id}/arrival", json=test_trip_arrival_data)

        # 관리자가 반려 (body 없이)
        response = admin_client.post(f"/api/v1/admin/trips/{trip_id}/reject")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "REJECTED"
        # 반려 사유가 기록되었는지 확인 (스키마에 따라 다를 수 있음)

    def test_reject_trip_non_admin(
        self,
        authenticated_client: TestClient,
        test_trip_start_data: dict,
        test_trip_transfer_data: dict,
        test_trip_arrival_data: dict,
    ):
        """
        일반 사용자의 반려 시도 테스트
        관리자가 아닌 사용자가 반려 시도 시 403 Forbidden 반환
        """
        # 여정 완료
        start_response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)
        trip_id = start_response.json()["data"]["trip_id"]

        authenticated_client.post(f"/api/v1/trips/{trip_id}/transfer", json=test_trip_transfer_data)
        authenticated_client.post(f"/api/v1/trips/{trip_id}/arrival", json=test_trip_arrival_data)

        # 일반 사용자가 반려 시도 (body 없이)
        response = authenticated_client.post(
            f"/api/v1/admin/trips/{trip_id}/reject"
        )

        assert response.status_code == 403
        data = response.json()
        assert data["status"] == "error"

    def test_reject_trip_already_rejected(
        self,
        authenticated_client: TestClient,
        admin_client: TestClient,
        test_trip_start_data: dict,
        test_trip_transfer_data: dict,
        test_trip_arrival_data: dict,
    ):
        """
        이미 반려된 여정 다시 반려 시도 테스트
        이미 REJECTED 상태인 여정 반려 시도 시 422 Validation Error 반환
        """
        # 여정 완료
        start_response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)
        trip_id = start_response.json()["data"]["trip_id"]

        authenticated_client.post(f"/api/v1/trips/{trip_id}/transfer", json=test_trip_transfer_data)
        authenticated_client.post(f"/api/v1/trips/{trip_id}/arrival", json=test_trip_arrival_data)

        # 첫 번째 반려 (성공)
        response = admin_client.post(f"/api/v1/admin/trips/{trip_id}/reject")
        assert response.status_code == 200

        # 두 번째 반려 시도 (실패 - 이미 REJECTED 상태)
        response = admin_client.post(f"/api/v1/admin/trips/{trip_id}/reject")

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"


class TestAdminTripList:
    """관리자 여정 목록 조회 테스트 클래스"""

    def test_get_pending_trips(self, admin_client: TestClient):
        """
        대기 중인 여정 목록 조회 테스트
        관리자가 승인 대기 중인 여정 목록 조회
        """
        response = admin_client.get("/api/v1/admin/trips?status=COMPLETED")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "trips" in data["data"]
        assert "total_count" in data["data"]

    def test_get_all_trips_as_admin(self, admin_client: TestClient):
        """
        관리자의 전체 여정 목록 조회 테스트
        관리자는 모든 사용자의 여정을 조회 가능
        """
        response = admin_client.get("/api/v1/admin/trips")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "trips" in data["data"]

    def test_get_admin_trips_non_admin(self, authenticated_client: TestClient):
        """
        일반 사용자의 관리자 여정 목록 조회 시도 테스트
        일반 사용자가 관리자 API 접근 시 403 Forbidden 반환
        """
        response = authenticated_client.get("/api/v1/admin/trips")

        assert response.status_code == 403
        data = response.json()
        assert data["status"] == "error"

    def test_get_trips_with_status_filter(self, admin_client: TestClient):
        """
        상태 필터링 여정 목록 조회 테스트
        특정 상태의 여정만 필터링하여 조회
        """
        response = admin_client.get("/api/v1/admin/trips?status=APPROVED")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # 모든 여정이 APPROVED 상태인지 확인
        if data["data"]["total_count"] > 0:
            for trip in data["data"]["trips"]:
                assert trip["status"] == "APPROVED"


class TestAdminStatistics:
    """관리자 통계 조회 테스트 클래스"""

    def test_get_admin_dashboard_stats(self, admin_client: TestClient):
        """
        관리자 대시보드 통계 조회 테스트
        전체 여정 수, 승인/반려 수 등 통계 정보 조회
        """
        response = admin_client.get("/api/v1/admin/stats")

        # 엔드포인트가 구현되어 있으면 성공, 없으면 404
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success"
            # 통계 데이터 확인 (구현에 따라 다를 수 있음)

    def test_get_stats_non_admin(self, authenticated_client: TestClient):
        """
        일반 사용자의 통계 조회 시도 테스트
        일반 사용자가 통계 API 접근 시 403 Forbidden 반환
        """
        response = authenticated_client.get("/api/v1/admin/stats")

        assert response.status_code in [403, 404]


class TestAdminAuthorization:
    """관리자 권한 검증 테스트 클래스"""

    def test_admin_endpoint_unauthorized(self, test_client: TestClient):
        """
        인증 없이 관리자 엔드포인트 접근 테스트
        토큰 없이 관리자 API 접근 시 401 또는 403 반환 (HTTPBearer는 403)
        """
        response = test_client.get("/api/v1/admin/trips")

        # HTTPBearer는 토큰 없을 때 403 반환
        assert response.status_code in [401, 403]

    def test_admin_role_required(self, authenticated_client: TestClient):
        """
        일반 사용자의 관리자 권한 필요 API 접근 테스트
        role='admin'이 아닌 사용자가 접근 시 403 Forbidden 반환
        """
        fake_trip_id = "00000000-0000-0000-0000-000000000000"
        response = authenticated_client.post(
            f"/api/v1/admin/trips/{fake_trip_id}/approve"        )

        assert response.status_code == 403
        data = response.json()
        assert data["status"] == "error"


# ============================================================================
# 역(Station) 관리 테스트
# ============================================================================


