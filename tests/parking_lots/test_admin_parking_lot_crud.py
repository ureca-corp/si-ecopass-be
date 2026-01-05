"""
주차장(Parking Lot) 관리 API 테스트

관리자 전용 주차장 생성, 수정, 삭제 엔드포인트 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestAdminParkingLotCreate:
    """관리자 주차장 생성 테스트 클래스"""

    def test_create_parking_lot_success(self, admin_client: TestClient, test_client: TestClient):
        """
        주차장 생성 성공 테스트
        관리자가 새 주차장을 생성하면 201 Created 반환
        """
        # 먼저 역 목록에서 station_id 가져오기
        stations_response = test_client.get("/api/v1/stations?limit=1")
        stations = stations_response.json()["data"]["stations"]
        assert len(stations) > 0, "테스트를 위한 역이 필요합니다"
        station_id = stations[0]["id"]

        # 주차장 생성 (주소만 제공, 좌표는 자동 계산됨)
        parking_lot_data = {
            "station_id": station_id,
            "name": "테스트주차장_생성",
            "address": "대구광역시 중구 동성로2가 123",
            "fee_info": "1시간 1,000원",
        }
        response = admin_client.post("/api/v1/admin/parking-lots", json=parking_lot_data)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["name"] == "테스트주차장_생성"
        assert data["data"]["station_id"] == station_id
        # distance_to_station_m은 자동 계산됨 (PostGIS)
        assert data["data"]["distance_to_station_m"] is not None

        # 생성된 주차장 ID 저장 (정리용)
        created_id = data["data"]["id"]

        # 정리: 생성된 주차장 삭제
        admin_client.delete(f"/api/v1/admin/parking-lots/{created_id}")

    def test_create_parking_lot_invalid_station(self, admin_client: TestClient):
        """
        존재하지 않는 역에 주차장 생성 시도 테스트
        유효하지 않은 station_id로 생성 시도 시 404 Not Found 반환
        """
        fake_station_id = "00000000-0000-0000-0000-000000000000"
        parking_lot_data = {
            "station_id": fake_station_id,
            "name": "잘못된주차장",
            "address": "대구광역시 중구 동성로2가 123",
        }
        response = admin_client.post("/api/v1/admin/parking-lots", json=parking_lot_data)

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"

    def test_create_parking_lot_non_admin(self, authenticated_client: TestClient, test_client: TestClient):
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

    def test_update_parking_lot_success(self, admin_client: TestClient, test_client: TestClient):
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

    def test_delete_parking_lot_success(self, admin_client: TestClient, test_client: TestClient):
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

    def test_delete_station_cascades_parking_lots(self, admin_client: TestClient):
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
