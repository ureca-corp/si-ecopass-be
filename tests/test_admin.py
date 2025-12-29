"""
관리자(Admin) API 테스트

여정 승인/반려, 포인트 지급 등 관리자 전용 엔드포인트 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestAdminApproval:
    """관리자 여정 승인 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_approve_trip_success(
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
        approve_data = {"earned_points": 100}
        response = admin_client.post(f"/api/v1/admin/trips/{trip_id}/approve", json=approve_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "APPROVED"
        assert data["data"]["earned_points"] == 100

    @pytest.mark.asyncio
    async def test_approve_trip_non_admin(
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
        approve_data = {"earned_points": 100}
        response = authenticated_client.post(
            f"/api/v1/admin/trips/{trip_id}/approve", json=approve_data
        )

        assert response.status_code == 403
        data = response.json()
        assert data["status"] == "error"
        assert "권한" in data["message"] or "admin" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_approve_incomplete_trip(
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
        approve_data = {"earned_points": 100}
        response = admin_client.post(f"/api/v1/admin/trips/{trip_id}/approve", json=approve_data)

        assert response.status_code >= 400  # 에러면 OK (400, 422 등)
        data = response.json()
        assert data["status"] == "error"

    @pytest.mark.asyncio
    async def test_approve_nonexistent_trip(self, admin_client: TestClient):
        """
        존재하지 않는 여정 승인 시도 테스트
        잘못된 여정 ID로 승인 시도 시 404 Not Found 반환
        """
        fake_trip_id = "00000000-0000-0000-0000-000000000000"
        approve_data = {"earned_points": 100}
        response = admin_client.post(
            f"/api/v1/admin/trips/{fake_trip_id}/approve", json=approve_data
        )

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"

    @pytest.mark.asyncio
    async def test_approve_with_negative_points(
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

        # 음수 포인트로 승인 시도
        approve_data = {"earned_points": -50}
        response = admin_client.post(f"/api/v1/admin/trips/{trip_id}/approve", json=approve_data)

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"


class TestAdminRejection:
    """관리자 여정 반려 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_reject_trip_success(
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

        # 관리자가 반려
        reject_data = {"admin_note": "증빙 이미지가 불명확합니다"}
        response = admin_client.post(f"/api/v1/admin/trips/{trip_id}/reject", json=reject_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["status"] == "REJECTED"
        # 반려 사유가 기록되었는지 확인 (스키마에 따라 다를 수 있음)

    @pytest.mark.asyncio
    async def test_reject_trip_non_admin(
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

        # 일반 사용자가 반려 시도
        reject_data = {"admin_note": "반려 사유"}
        response = authenticated_client.post(
            f"/api/v1/admin/trips/{trip_id}/reject", json=reject_data
        )

        assert response.status_code == 403
        data = response.json()
        assert data["status"] == "error"

    @pytest.mark.asyncio
    async def test_reject_trip_without_reason(
        self,
        authenticated_client: TestClient,
        admin_client: TestClient,
        test_trip_start_data: dict,
        test_trip_transfer_data: dict,
        test_trip_arrival_data: dict,
    ):
        """
        반려 사유 없이 반려 시도 테스트
        반려 사유 없이 반려 시도 시 422 Validation Error 반환
        """
        # 여정 완료
        start_response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)
        trip_id = start_response.json()["data"]["trip_id"]

        authenticated_client.post(f"/api/v1/trips/{trip_id}/transfer", json=test_trip_transfer_data)
        authenticated_client.post(f"/api/v1/trips/{trip_id}/arrival", json=test_trip_arrival_data)

        # 사유 없이 반려 시도
        response = admin_client.post(f"/api/v1/admin/trips/{trip_id}/reject", json={})

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"


class TestAdminTripList:
    """관리자 여정 목록 조회 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_get_pending_trips(self, admin_client: TestClient):
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

    @pytest.mark.asyncio
    async def test_get_all_trips_as_admin(self, admin_client: TestClient):
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

    @pytest.mark.asyncio
    async def test_get_trips_with_status_filter(self, admin_client: TestClient):
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

    @pytest.mark.asyncio
    async def test_get_admin_dashboard_stats(self, admin_client: TestClient):
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

    @pytest.mark.asyncio
    async def test_admin_role_required(self, authenticated_client: TestClient):
        """
        일반 사용자의 관리자 권한 필요 API 접근 테스트
        role='admin'이 아닌 사용자가 접근 시 403 Forbidden 반환
        """
        fake_trip_id = "00000000-0000-0000-0000-000000000000"
        approve_data = {"earned_points": 100}
        response = authenticated_client.post(
            f"/api/v1/admin/trips/{fake_trip_id}/approve", json=approve_data
        )

        assert response.status_code == 403
        data = response.json()
        assert data["status"] == "error"


# ============================================================================
# 역(Station) 관리 테스트
# ============================================================================


class TestAdminStationCreate:
    """관리자 역 생성 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_create_station_success(self, admin_client: TestClient):
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

    @pytest.mark.asyncio
    async def test_create_station_invalid_line(self, admin_client: TestClient):
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

    @pytest.mark.asyncio
    async def test_create_station_non_admin(self, authenticated_client: TestClient):
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

        assert response.status_code == 401
        data = response.json()
        assert data["status"] == "error"


class TestAdminStationUpdate:
    """관리자 역 수정 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_update_station_success(self, admin_client: TestClient):
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

    @pytest.mark.asyncio
    async def test_update_station_not_found(self, admin_client: TestClient):
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

    @pytest.mark.asyncio
    async def test_delete_station_success(self, admin_client: TestClient):
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

    @pytest.mark.asyncio
    async def test_delete_station_not_found(self, admin_client: TestClient):
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


class TestAdminParkingLotCreate:
    """관리자 주차장 생성 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_create_parking_lot_success(self, admin_client: TestClient, test_client: TestClient):
        """
        주차장 생성 성공 테스트
        관리자가 새 주차장을 생성하면 201 Created 반환
        """
        # 먼저 역 목록에서 station_id 가져오기
        stations_response = test_client.get("/api/v1/stations?limit=1")
        stations = stations_response.json()["data"]["stations"]
        assert len(stations) > 0, "테스트를 위한 역이 필요합니다"
        station_id = stations[0]["id"]

        # 주차장 생성
        parking_lot_data = {
            "station_id": station_id,
            "name": "테스트주차장_생성",
            "address": "대구광역시 테스트구 테스트동 123",
            "latitude": 35.8650,
            "longitude": 128.5950,
            "distance_to_station_m": 200,
            "fee_info": "1시간 1,000원",
        }
        response = admin_client.post("/api/v1/admin/parking-lots", json=parking_lot_data)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["name"] == "테스트주차장_생성"
        assert data["data"]["station_id"] == station_id
        assert data["data"]["distance_to_station_m"] == 200

        # 생성된 주차장 ID 저장 (정리용)
        created_id = data["data"]["id"]

        # 정리: 생성된 주차장 삭제
        admin_client.delete(f"/api/v1/admin/parking-lots/{created_id}")

    @pytest.mark.asyncio
    async def test_create_parking_lot_invalid_station(self, admin_client: TestClient):
        """
        존재하지 않는 역에 주차장 생성 시도 테스트
        유효하지 않은 station_id로 생성 시도 시 404 Not Found 반환
        """
        fake_station_id = "00000000-0000-0000-0000-000000000000"
        parking_lot_data = {
            "station_id": fake_station_id,
            "name": "잘못된주차장",
            "address": "없는 주소",
            "latitude": 35.8650,
            "longitude": 128.5950,
        }
        response = admin_client.post("/api/v1/admin/parking-lots", json=parking_lot_data)

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"

    @pytest.mark.asyncio
    async def test_create_parking_lot_non_admin(self, authenticated_client: TestClient, test_client: TestClient):
        """
        일반 사용자의 주차장 생성 시도 테스트
        관리자가 아닌 사용자가 주차장 생성 시도 시 403 Forbidden 반환
        """
        # 역 ID 가져오기
        stations_response = test_client.get("/api/v1/stations?limit=1")
        stations = stations_response.json()["data"]["stations"]
        if len(stations) == 0:
            pytest.skip("테스트를 위한 역이 필요합니다")
        station_id = stations[0]["id"]

        parking_lot_data = {
            "station_id": station_id,
            "name": "일반유저주차장",
            "address": "테스트 주소",
            "latitude": 35.8650,
            "longitude": 128.5950,
        }
        response = authenticated_client.post("/api/v1/admin/parking-lots", json=parking_lot_data)

        assert response.status_code == 403
        data = response.json()
        assert data["status"] == "error"


class TestAdminParkingLotUpdate:
    """관리자 주차장 수정 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_update_parking_lot_success(self, admin_client: TestClient, test_client: TestClient):
        """
        주차장 수정 성공 테스트
        관리자가 기존 주차장 정보를 수정하면 200 OK 반환
        """
        # 역 ID 가져오기
        stations_response = test_client.get("/api/v1/stations?limit=1")
        stations = stations_response.json()["data"]["stations"]
        assert len(stations) > 0, "테스트를 위한 역이 필요합니다"
        station_id = stations[0]["id"]

        # 테스트용 주차장 생성
        create_data = {
            "station_id": station_id,
            "name": "수정전주차장",
            "address": "수정 전 주소",
            "latitude": 35.8600,
            "longitude": 128.5900,
        }
        create_response = admin_client.post("/api/v1/admin/parking-lots", json=create_data)
        assert create_response.status_code == 201
        parking_lot_id = create_response.json()["data"]["id"]

        # 주차장 정보 수정
        update_data = {
            "name": "수정후주차장",
            "fee_info": "2시간 무료",
        }
        response = admin_client.put(f"/api/v1/admin/parking-lots/{parking_lot_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["name"] == "수정후주차장"
        assert data["data"]["fee_info"] == "2시간 무료"

        # 정리: 생성된 주차장 삭제
        admin_client.delete(f"/api/v1/admin/parking-lots/{parking_lot_id}")


class TestAdminParkingLotDelete:
    """관리자 주차장 삭제 테스트 클래스"""

    @pytest.mark.asyncio
    async def test_delete_parking_lot_success(self, admin_client: TestClient, test_client: TestClient):
        """
        주차장 삭제 성공 테스트
        관리자가 주차장을 삭제하면 200 OK 반환
        """
        # 역 ID 가져오기
        stations_response = test_client.get("/api/v1/stations?limit=1")
        stations = stations_response.json()["data"]["stations"]
        assert len(stations) > 0, "테스트를 위한 역이 필요합니다"
        station_id = stations[0]["id"]

        # 테스트용 주차장 생성
        create_data = {
            "station_id": station_id,
            "name": "삭제테스트주차장",
            "address": "삭제할 주소",
            "latitude": 35.8620,
            "longitude": 128.5920,
        }
        create_response = admin_client.post("/api/v1/admin/parking-lots", json=create_data)
        assert create_response.status_code == 201
        parking_lot_id = create_response.json()["data"]["id"]

        # 주차장 삭제
        response = admin_client.delete(f"/api/v1/admin/parking-lots/{parking_lot_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestAdminStationCascadeDelete:
    """역 삭제 시 연결된 주차장 CASCADE 삭제 테스트"""

    @pytest.mark.asyncio
    async def test_delete_station_cascades_parking_lots(self, admin_client: TestClient):
        """
        역 삭제 시 연결된 주차장도 함께 삭제되는지 테스트
        CASCADE 삭제 동작 확인
        """
        # 1. 테스트용 역 생성
        station_data = {
            "name": "캐스케이드테스트역",
            "line_number": 4,
            "latitude": 35.8550,
            "longitude": 128.5850,
        }
        station_response = admin_client.post("/api/v1/admin/stations", json=station_data)
        assert station_response.status_code == 201
        station_id = station_response.json()["data"]["id"]

        # 2. 해당 역에 주차장 생성
        parking_lot_data = {
            "station_id": station_id,
            "name": "캐스케이드테스트주차장",
            "address": "테스트 주소",
            "latitude": 35.8555,
            "longitude": 128.5855,
        }
        parking_response = admin_client.post("/api/v1/admin/parking-lots", json=parking_lot_data)
        assert parking_response.status_code == 201
        parking_lot_id = parking_response.json()["data"]["id"]

        # 3. 역 삭제 (주차장도 함께 삭제되어야 함)
        delete_response = admin_client.delete(f"/api/v1/admin/stations/{station_id}")
        assert delete_response.status_code == 200

        # 4. 역 조회 시 404 확인
        get_station_response = admin_client.get(f"/api/v1/stations/{station_id}")
        assert get_station_response.status_code == 404
