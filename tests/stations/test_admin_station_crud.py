"""
역(Station) 관리 API 테스트

관리자 전용 역 생성, 수정, 삭제 엔드포인트 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestAdminStationCreate:
    """관리자 역 생성 테스트 클래스"""

    def test_create_station_success(self, admin_client: TestClient):
        """
        역 생성 성공 테스트
        관리자가 새 역을 생성하면 201 Created 반환
        """
        station_data = {
            "name": "테스트역_생성",
            "line_number": 1,
            "latitude": 35.8700,
            "longitude": 128.6000,
        }
        response = admin_client.post("/api/v1/admin/stations", json=station_data)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["name"] == "테스트역_생성"
        assert data["data"]["line_number"] == 1
        assert data["data"]["latitude"] == 35.8700
        assert data["data"]["longitude"] == 128.6000

        # 생성된 역 ID 저장 (정리용)
        created_id = data["data"]["id"]

        # 정리: 생성된 역 삭제
        admin_client.delete(f"/api/v1/admin/stations/{created_id}")

    def test_create_station_invalid_line(self, admin_client: TestClient):
        """
        잘못된 노선 번호로 역 생성 시 422 Validation Error 반환
        """
        station_data = {
            "name": "잘못된역",
            "line_number": 99,  # 유효하지 않은 노선
            "latitude": 35.8700,
            "longitude": 128.6000,
        }
        response = admin_client.post("/api/v1/admin/stations", json=station_data)

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"

    def test_create_station_non_admin(self, authenticated_client: TestClient):
        """
        일반 사용자의 역 생성 시도 테스트
        관리자가 아닌 사용자가 역 생성 시도 시 403 Forbidden 반환
        """
        station_data = {
            "name": "일반유저역",
            "line_number": 1,
            "latitude": 35.8700,
            "longitude": 128.6000,
        }
        response = authenticated_client.post("/api/v1/admin/stations", json=station_data)

        assert response.status_code == 403
        data = response.json()
        assert data["status"] == "error"

    def test_create_station_unauthorized(self, test_client: TestClient):
        """
        인증 없이 역 생성 시도 테스트
        토큰 없이 역 생성 시도 시 401 Unauthorized 반환
        """
        station_data = {
            "name": "비인증역",
            "line_number": 1,
            "latitude": 35.8700,
            "longitude": 128.6000,
        }
        response = test_client.post("/api/v1/admin/stations", json=station_data)

        # HTTPBearer returns 403 when no credentials are provided
        assert response.status_code in [401, 403]
        data = response.json()
        # FastAPI's HTTPBearer may return a different error format
        assert data.get("status") == "error" or "detail" in data


class TestAdminStationUpdate:
    """관리자 역 수정 테스트 클래스"""

    def test_update_station_success(self, admin_client: TestClient):
        """
        역 수정 성공 테스트
        관리자가 기존 역 정보를 수정하면 200 OK 반환
        """
        # 먼저 테스트용 역 생성
        create_data = {
            "name": "수정전역",
            "line_number": 2,
            "latitude": 35.8500,
            "longitude": 128.5500,
        }
        create_response = admin_client.post("/api/v1/admin/stations", json=create_data)
        assert create_response.status_code == 201
        station_id = create_response.json()["data"]["id"]

        # 역 정보 수정
        update_data = {
            "name": "수정후역",
            "line_number": 3,
        }
        response = admin_client.put(f"/api/v1/admin/stations/{station_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["name"] == "수정후역"
        assert data["data"]["line_number"] == 3

        # 정리: 생성된 역 삭제
        admin_client.delete(f"/api/v1/admin/stations/{station_id}")

    def test_update_station_not_found(self, admin_client: TestClient):
        """
        존재하지 않는 역 수정 시도 테스트
        잘못된 역 ID로 수정 시도 시 404 Not Found 반환
        """
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"name": "없는역수정"}
        response = admin_client.put(f"/api/v1/admin/stations/{fake_id}", json=update_data)

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"


class TestAdminStationDelete:
    """관리자 역 삭제 테스트 클래스"""

    def test_delete_station_success(self, admin_client: TestClient):
        """
        역 삭제 성공 테스트
        관리자가 역을 삭제하면 200 OK 반환
        """
        # 먼저 테스트용 역 생성
        create_data = {
            "name": "삭제테스트역",
            "line_number": 1,
            "latitude": 35.8600,
            "longitude": 128.5800,
        }
        create_response = admin_client.post("/api/v1/admin/stations", json=create_data)
        assert create_response.status_code == 201
        station_id = create_response.json()["data"]["id"]

        # 역 삭제
        response = admin_client.delete(f"/api/v1/admin/stations/{station_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # 삭제 확인: 조회 시 404 반환
        get_response = admin_client.get(f"/api/v1/stations/{station_id}")
        assert get_response.status_code == 404

    def test_delete_station_not_found(self, admin_client: TestClient):
        """
        존재하지 않는 역 삭제 시도 테스트
        잘못된 역 ID로 삭제 시도 시 404 Not Found 반환
        """
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = admin_client.delete(f"/api/v1/admin/stations/{fake_id}")

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"


# ============================================================================
# 주차장(Parking Lot) 관리 테스트
# ============================================================================


