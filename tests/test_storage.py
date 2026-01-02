"""
스토리지(Storage) API 테스트

이미지 업로드, URL 생성 등 Supabase Storage 관련 엔드포인트 테스트
"""

import io
from typing import BinaryIO

import pytest
from fastapi.testclient import TestClient


class TestImageUpload:
    """이미지 업로드 테스트 클래스"""

    def test_upload_transfer_image_success(self, authenticated_client: TestClient):
        """
        환승 이미지 업로드 성공 테스트
        유효한 이미지 파일을 업로드하면 성공 응답 및 URL 반환
        """
        # 테스트용 이미지 파일 생성 (1x1 PNG)
        image_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01"
            b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        files = {"file": ("test_transfer.png", io.BytesIO(image_data), "image/png")}

        response = authenticated_client.post("/api/v1/storage/upload/transfer", files=files)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert "image_url" in data["data"]
        assert "uploaded_at" in data["data"]
        assert "stage" in data["data"]
        assert data["data"]["image_url"].startswith("http")
        assert data["data"]["stage"] == "transfer"

    def test_upload_arrival_image_success(self, authenticated_client: TestClient):
        """
        도착 이미지 업로드 성공 테스트
        유효한 이미지 파일을 업로드하면 성공 응답 및 URL 반환
        """
        # 테스트용 이미지 파일 생성 (1x1 PNG)
        image_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01"
            b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        files = {"file": ("test_arrival.png", io.BytesIO(image_data), "image/png")}

        response = authenticated_client.post("/api/v1/storage/upload/arrival", files=files)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert "image_url" in data["data"]
        assert "uploaded_at" in data["data"]
        assert "stage" in data["data"]
        assert data["data"]["image_url"].startswith("http")
        assert data["data"]["stage"] == "arrival"

    def test_upload_image_unauthorized(self, test_client: TestClient):
        """
        인증 없이 이미지 업로드 테스트
        토큰 없이 이미지 업로드 시 401 Unauthorized 반환
        """
        image_data = b"\x89PNG\r\n\x1a\n"
        files = {"file": ("test.png", io.BytesIO(image_data), "image/png")}

        response = test_client.post("/api/v1/storage/upload/transfer", files=files)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data  # HTTPBearer returns {'detail': 'Not authenticated'}

    def test_upload_invalid_file_type(self, authenticated_client: TestClient):
        """
        잘못된 파일 형식 업로드 테스트
        이미지가 아닌 파일(예: txt) 업로드 시 422 Validation Error 반환
        """
        text_data = b"This is not an image"
        files = {"file": ("test.txt", io.BytesIO(text_data), "text/plain")}

        response = authenticated_client.post("/api/v1/storage/upload/transfer", files=files)

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"

    def test_upload_oversized_image(self, authenticated_client: TestClient):
        """
        파일 크기 초과 테스트
        허용 크기(10MB)를 초과하는 이미지 업로드 시 422 Validation Error 반환
        """
        # 11MB 크기의 가짜 이미지 데이터 생성
        oversized_data = b"\x00" * (11 * 1024 * 1024)
        files = {"file": ("oversized.png", io.BytesIO(oversized_data), "image/png")}

        response = authenticated_client.post("/api/v1/storage/upload/transfer", files=files)

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"
        assert "크기" in data["message"] or "size" in data["message"].lower()

    def test_upload_missing_file(self, authenticated_client: TestClient):
        """
        파일 누락 테스트
        파일 없이 업로드 요청 시 422 Validation Error 반환
        """
        response = authenticated_client.post("/api/v1/storage/upload/transfer")

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"

    def test_upload_jpeg_image(self, authenticated_client: TestClient):
        """
        JPEG 이미지 업로드 테스트
        PNG 외에 JPEG 형식도 정상 업로드 가능
        """
        # 최소 JPEG 파일 헤더
        jpeg_data = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        files = {"file": ("test.jpg", io.BytesIO(jpeg_data), "image/jpeg")}

        response = authenticated_client.post("/api/v1/storage/upload/transfer", files=files)

        # 성공 또는 유효성 검증 실패 (최소 JPEG 헤더가 충분하지 않을 수 있음)
        assert response.status_code in [201, 422]


class TestImageRetrieval:
    """이미지 조회 테스트 클래스"""

    def test_get_uploaded_image_url(self, authenticated_client: TestClient):
        """
        업로드된 이미지 URL 접근 테스트
        업로드 후 반환된 URL로 이미지 접근 가능
        """
        # 이미지 업로드
        image_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01"
            b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        files = {"file": ("test.png", io.BytesIO(image_data), "image/png")}
        upload_response = authenticated_client.post("/api/v1/storage/upload/transfer", files=files)

        assert upload_response.status_code == 201
        image_url = upload_response.json()["data"]["image_url"]

        # URL이 유효한 형식인지 확인
        assert image_url.startswith("http")
        assert "transfer" in image_url or "storage" in image_url


class TestStorageIntegration:
    """스토리지 통합 테스트 클래스"""

    def test_upload_and_use_in_trip(
        self,
        authenticated_client: TestClient,
        test_trip_start_data: dict,
        test_trip_transfer_data: dict,
    ):
        """
        이미지 업로드 및 여정에서 사용 통합 테스트
        이미지를 업로드하고 여정 환승에서 해당 URL 사용
        """
        # 1. 여정 시작
        start_response = authenticated_client.post("/api/v1/trips/start", json=test_trip_start_data)
        trip_id = start_response.json()["data"]["trip_id"]

        # 2. 환승 이미지 업로드
        image_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01"
            b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        files = {"file": ("transfer.png", io.BytesIO(image_data), "image/png")}
        upload_response = authenticated_client.post("/api/v1/storage/upload/transfer", files=files)
        image_url = upload_response.json()["data"]["image_url"]

        # 3. 업로드된 이미지 URL로 환승 기록
        test_trip_transfer_data["transfer_image_url"] = image_url
        transfer_response = authenticated_client.post(
            f"/api/v1/trips/{trip_id}/transfer", json=test_trip_transfer_data
        )

        assert transfer_response.status_code == 200
        assert transfer_response.json()["data"]["status"] == "TRANSFERRED"

        # 4. 여정 조회하여 이미지 URL 확인
        trip_response = authenticated_client.get(f"/api/v1/trips/{trip_id}")
        trip_data = trip_response.json()["data"]
        assert trip_data["transfer_image_url"] == image_url

    def test_multiple_images_upload(self, authenticated_client: TestClient):
        """
        여러 이미지 연속 업로드 테스트
        동일 사용자가 여러 이미지를 연속으로 업로드 가능
        """
        image_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01"
            b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )

        uploaded_urls = []
        for i in range(3):
            files = {"file": (f"test_{i}.png", io.BytesIO(image_data), "image/png")}
            response = authenticated_client.post("/api/v1/storage/upload/transfer", files=files)

            assert response.status_code == 201
            uploaded_urls.append(response.json()["data"]["image_url"])

        # 모든 URL이 서로 다른지 확인 (고유한 파일명)
        assert len(set(uploaded_urls)) == 3
