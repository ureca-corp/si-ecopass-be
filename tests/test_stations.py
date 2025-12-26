"""
역/주차장 API 테스트

지하철 역 조회, 주차장 조회 등 역/주차장 관련 엔드포인트 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestStationList:
    """역 목록 조회 테스트 클래스"""

    def test_get_stations_success(self, test_client: TestClient):
        """
        전체 역 목록 조회 테스트
        모든 지하철 역 목록을 성공적으로 조회
        """
        response = test_client.get("/api/v1/stations")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "stations" in data["data"]
        assert "total_count" in data["data"]
        assert isinstance(data["data"]["stations"], list)
        assert data["data"]["total_count"] >= 0

    def test_get_stations_with_line_filter(self, test_client: TestClient):
        """
        호선 필터링 역 목록 조회 테스트
        특정 호선의 역만 필터링하여 조회
        """
        response = test_client.get("/api/v1/stations?line=1")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

        # 1호선 역만 반환되는지 확인
        if data["data"]["total_count"] > 0:
            for station in data["data"]["stations"]:
                assert station["line_number"] == 1

    def test_get_stations_with_pagination(self, test_client: TestClient):
        """
        페이지네이션 테스트
        limit과 offset 파라미터로 페이지네이션 적용
        """
        response = test_client.get("/api/v1/stations?limit=5&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]["stations"]) <= 5

    def test_get_stations_invalid_line(self, test_client: TestClient):
        """
        잘못된 호선 필터 테스트
        존재하지 않는 호선으로 조회 시 유효성 검증 에러 반환
        """
        response = test_client.get("/api/v1/stations?line=99")

        # 잘못된 호선 번호는 유효성 검증 에러 발생
        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"


class TestStationDetail:
    """역 상세 정보 조회 테스트 클래스"""

    def test_get_station_by_id_success(self, test_client: TestClient):
        """
        역 ID로 상세 정보 조회 테스트
        유효한 역 ID로 조회 시 상세 정보 반환
        """
        # 먼저 역 목록을 조회하여 ID 가져오기
        list_response = test_client.get("/api/v1/stations?limit=1")
        stations = list_response.json()["data"]["stations"]

        if len(stations) > 0:
            station_id = stations[0]["id"]
            response = test_client.get(f"/api/v1/stations/{station_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["id"] == station_id
            assert "name" in data["data"]
            assert "line_number" in data["data"]

    @pytest.mark.skip(reason="Name search feature not yet implemented")
    def test_get_station_by_name_success(self, test_client: TestClient):
        """
        역 이름으로 검색 테스트
        역 이름으로 검색 시 매칭되는 역 정보 반환
        """
        response = test_client.get("/api/v1/stations?name=대구")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        # 대구가 포함된 역명 검색 결과 확인
        if data["data"]["total_count"] > 0:
            for station in data["data"]["stations"]:
                assert "대구" in station["name"] or station["name"].startswith("대구")

    def test_get_station_not_found(self, test_client: TestClient):
        """
        존재하지 않는 역 조회 테스트
        잘못된 역 ID로 조회 시 404 Not Found 반환
        """
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = test_client.get(f"/api/v1/stations/{fake_id}")

        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"


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
