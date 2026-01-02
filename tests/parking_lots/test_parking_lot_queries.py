"""
주차장 조회 API 테스트

주차장 목록 조회, 주변 역 검색 등 주차장 관련 엔드포인트 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestParkingLots:
    """주차장 조회 테스트 클래스"""

    def test_get_parking_lots_by_station(self, test_client: TestClient):
        """
        특정 역의 주차장 목록 조회 테스트
        역 ID로 해당 역의 주차장 목록 조회
        """
        # 먼저 역 목록 조회
        list_response = test_client.get("/api/v1/stations?limit=1")
        stations = list_response.json()["data"]["stations"]

        if len(stations) > 0:
            station_id = stations[0]["id"]
            response = test_client.get(f"/api/v1/stations/{station_id}/parking-lots")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "data" in data
            assert "parking_lots" in data["data"]
            assert isinstance(data["data"]["parking_lots"], list)

    def test_get_parking_lots_empty_station(self, test_client: TestClient):
        """
        주차장이 없는 역 조회 테스트
        주차장이 없는 역 조회 시 빈 목록 반환
        """
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = test_client.get(f"/api/v1/stations/{fake_id}/parking-lots")

        # 404 또는 빈 목록 응답
        assert response.status_code in [200, 404]

    @pytest.mark.skip(reason="Nearby stations search feature not yet implemented")
    def test_get_nearby_stations(self, test_client: TestClient):
        """
        주변 역 검색 테스트
        현재 위치 기준 근처 역 검색
        """
        # 대구역 좌표
        latitude = 35.8809
        longitude = 128.6286

        response = test_client.get(f"/api/v1/stations/nearby?latitude={latitude}&longitude={longitude}&radius=5000")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "stations" in data["data"]
        assert isinstance(data["data"]["stations"], list)

    @pytest.mark.skip(reason="Nearby stations search feature not yet implemented")
    def test_get_nearby_stations_invalid_coordinates(self, test_client: TestClient):
        """
        잘못된 좌표로 주변 역 검색 테스트
        유효하지 않은 위도/경도로 검색 시 422 Validation Error 반환
        """
        response = test_client.get("/api/v1/stations/nearby?latitude=999&longitude=999")

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"

    @pytest.mark.skip(reason="Nearby stations search feature not yet implemented")
    def test_get_nearby_stations_missing_params(self, test_client: TestClient):
        """
        필수 파라미터 누락 테스트
        위도/경도 없이 주변 역 검색 시 422 Validation Error 반환
        """
        response = test_client.get("/api/v1/stations/nearby")

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"
