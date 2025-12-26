"""
통합 테스트 (Integration Tests)

전체 사용자 여정을 시뮬레이션하는 시나리오 기반 테스트
회원가입 → 로그인 → 여정 시작 → 환승 → 도착 → 관리자 승인까지의 전체 플로우 검증
"""

import io

import pytest
from fastapi.testclient import TestClient


class TestFullUserJourney:
    """전체 사용자 여정 통합 테스트"""

    @pytest.mark.asyncio
    async def test_complete_trip_lifecycle(
        self,
        test_client: TestClient,
        test_user_data: dict,
        admin_client: TestClient,
    ):
        """
        전체 여정 생명주기 통합 테스트

        시나리오:
        1. 사용자 회원가입
        2. 로그인하여 JWT 토큰 획득
        3. 출발지에서 여정 시작
        4. 환승 이미지 업로드
        5. 환승 기록
        6. 도착 이미지 업로드
        7. 도착 기록
        8. 관리자가 여정 승인
        9. 사용자 포인트 증가 확인
        """
        # ============================================================
        # Phase 1: 사용자 회원가입 및 로그인
        # ============================================================

        # 1-1. 회원가입
        signup_response = test_client.post("/api/v1/auth/signup", json=test_user_data)
        assert signup_response.status_code == 201
        signup_data = signup_response.json()
        assert signup_data["status"] == "success"

        user_id = signup_data["data"]["user"]["id"]
        initial_points = signup_data["data"]["user"]["total_points"]
        assert initial_points == 0

        # 1-2. 로그인
        login_response = test_client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": test_user_data["password"]},
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        # 인증 헤더 설정
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # ============================================================
        # Phase 2: 여정 시작
        # ============================================================

        # 2-1. 출발지 정보 (대구역)
        start_data = {
            "latitude": 35.8809,
            "longitude": 128.6286,
        }

        start_response = test_client.post(
            "/api/v1/trips/start", json=start_data, headers=auth_headers
        )
        assert start_response.status_code == 201
        start_result = start_response.json()
        assert start_result["status"] == "success"

        trip_id = start_result["data"]["trip_id"]
        assert start_result["data"]["status"] == "DRIVING"

        # ============================================================
        # Phase 3: 환승
        # ============================================================

        # 3-1. 환승 증빙 이미지 업로드
        transfer_image_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01"
            b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        transfer_files = {
            "file": ("transfer_proof.png", io.BytesIO(transfer_image_data), "image/png")
        }

        upload_transfer_response = test_client.post(
            "/api/v1/storage/upload/transfer", files=transfer_files, headers=auth_headers
        )
        assert upload_transfer_response.status_code == 201
        transfer_image_url = upload_transfer_response.json()["data"]["url"]

        # 3-2. 환승 기록 (중앙로역)
        transfer_data = {
            "latitude": 35.8714,
            "longitude": 128.5988,
            "transfer_image_url": transfer_image_url,
        }

        transfer_response = test_client.post(
            f"/api/v1/trips/{trip_id}/transfer", json=transfer_data, headers=auth_headers
        )
        assert transfer_response.status_code == 200
        transfer_result = transfer_response.json()
        assert transfer_result["status"] == "success"
        assert transfer_result["data"]["status"] == "TRANSFERRED"

        # ============================================================
        # Phase 4: 도착
        # ============================================================

        # 4-1. 도착 증빙 이미지 업로드
        arrival_image_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01"
            b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        arrival_files = {
            "file": ("arrival_proof.png", io.BytesIO(arrival_image_data), "image/png")
        }

        upload_arrival_response = test_client.post(
            "/api/v1/storage/upload/arrival", files=arrival_files, headers=auth_headers
        )
        assert upload_arrival_response.status_code == 201
        arrival_image_url = upload_arrival_response.json()["data"]["url"]

        # 4-2. 도착 기록 (반월당역)
        arrival_data = {
            "latitude": 35.8569,
            "longitude": 128.5932,
            "arrival_image_url": arrival_image_url,
        }

        arrival_response = test_client.post(
            f"/api/v1/trips/{trip_id}/arrival", json=arrival_data, headers=auth_headers
        )
        assert arrival_response.status_code == 200
        arrival_result = arrival_response.json()
        assert arrival_result["status"] == "success"
        assert arrival_result["data"]["status"] == "COMPLETED"

        estimated_points = arrival_result["data"]["estimated_points"]
        assert estimated_points > 0

        # ============================================================
        # Phase 5: 관리자 승인
        # ============================================================

        # 5-1. 관리자가 여정 승인
        approve_data = {"points": estimated_points}
        approve_response = admin_client.post(
            f"/api/v1/admin/trips/{trip_id}/approve", json=approve_data
        )
        assert approve_response.status_code == 200
        approve_result = approve_response.json()
        assert approve_result["status"] == "success"
        assert approve_result["data"]["status"] == "APPROVED"
        assert approve_result["data"]["actual_points"] == estimated_points

        # ============================================================
        # Phase 6: 최종 검증
        # ============================================================

        # 6-1. 사용자 프로필 조회하여 포인트 증가 확인
        profile_response = test_client.get("/api/v1/auth/profile", headers=auth_headers)
        assert profile_response.status_code == 200
        profile_data = profile_response.json()["data"]
        assert profile_data["total_points"] == initial_points + estimated_points

        # 6-2. 여정 상세 정보 조회
        trip_response = test_client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)
        assert trip_response.status_code == 200
        trip_data = trip_response.json()["data"]
        assert trip_data["status"] == "APPROVED"
        assert trip_data["transfer_image_url"] == transfer_image_url
        assert trip_data["arrival_image_url"] == arrival_image_url
        assert trip_data["actual_points"] == estimated_points

        print("\n" + "=" * 60)
        print("✅ 전체 사용자 여정 통합 테스트 성공!")
        print(f"   - 사용자 ID: {user_id}")
        print(f"   - 여정 ID: {trip_id}")
        print(f"   - 획득 포인트: {estimated_points}")
        print("=" * 60 + "\n")


class TestMultipleTripsScenario:
    """여러 여정 시나리오 테스트"""

    @pytest.mark.asyncio
    async def test_multiple_trips_by_same_user(
        self, authenticated_client: TestClient, admin_client: TestClient
    ):
        """
        동일 사용자의 여러 여정 시나리오

        시나리오:
        1. 첫 번째 여정 완료 및 승인
        2. 두 번째 여정 시작 및 완료
        3. 두 번째 여정 승인
        4. 누적 포인트 확인
        """
        # 이미지 데이터
        image_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01"
            b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )

        # ============================================================
        # 첫 번째 여정
        # ============================================================

        # 여정 1 시작
        trip1_start = authenticated_client.post(
            "/api/v1/trips/start", json={"latitude": 35.8809, "longitude": 128.6286}
        )
        trip1_id = trip1_start.json()["data"]["trip_id"]

        # 환승 이미지 업로드
        files1 = {"file": ("t1.png", io.BytesIO(image_data), "image/png")}
        upload1 = authenticated_client.post("/api/v1/storage/upload/transfer", files=files1)
        image_url1 = upload1.json()["data"]["url"]

        # 환승
        authenticated_client.post(
            f"/api/v1/trips/{trip1_id}/transfer",
            json={"latitude": 35.8714, "longitude": 128.5988, "transfer_image_url": image_url1},
        )

        # 도착 이미지 업로드
        files2 = {"file": ("a1.png", io.BytesIO(image_data), "image/png")}
        upload2 = authenticated_client.post("/api/v1/storage/upload/arrival", files=files2)
        image_url2 = upload2.json()["data"]["url"]

        # 도착
        arrival1 = authenticated_client.post(
            f"/api/v1/trips/{trip1_id}/arrival",
            json={"latitude": 35.8569, "longitude": 128.5932, "arrival_image_url": image_url2},
        )
        points1 = arrival1.json()["data"]["estimated_points"]

        # 관리자 승인
        admin_client.post(f"/api/v1/admin/trips/{trip1_id}/approve", json={"points": points1})

        # ============================================================
        # 두 번째 여정
        # ============================================================

        # 여정 2 시작
        trip2_start = authenticated_client.post(
            "/api/v1/trips/start", json={"latitude": 35.8800, "longitude": 128.6300}
        )
        trip2_id = trip2_start.json()["data"]["trip_id"]

        # 환승 이미지 업로드
        files3 = {"file": ("t2.png", io.BytesIO(image_data), "image/png")}
        upload3 = authenticated_client.post("/api/v1/storage/upload/transfer", files=files3)
        image_url3 = upload3.json()["data"]["url"]

        # 환승
        authenticated_client.post(
            f"/api/v1/trips/{trip2_id}/transfer",
            json={"latitude": 35.8720, "longitude": 128.5990, "transfer_image_url": image_url3},
        )

        # 도착 이미지 업로드
        files4 = {"file": ("a2.png", io.BytesIO(image_data), "image/png")}
        upload4 = authenticated_client.post("/api/v1/storage/upload/arrival", files=files4)
        image_url4 = upload4.json()["data"]["url"]

        # 도착
        arrival2 = authenticated_client.post(
            f"/api/v1/trips/{trip2_id}/arrival",
            json={"latitude": 35.8570, "longitude": 128.5935, "arrival_image_url": image_url4},
        )
        points2 = arrival2.json()["data"]["estimated_points"]

        # 관리자 승인
        admin_client.post(f"/api/v1/admin/trips/{trip2_id}/approve", json={"points": points2})

        # ============================================================
        # 최종 검증
        # ============================================================

        # 누적 포인트 확인
        profile_response = authenticated_client.get("/api/v1/auth/profile")
        total_points = profile_response.json()["data"]["total_points"]
        assert total_points == points1 + points2

        # 여정 목록 조회
        trips_response = authenticated_client.get("/api/v1/trips")
        trips_data = trips_response.json()["data"]
        assert trips_data["total_count"] >= 2

        print("\n" + "=" * 60)
        print("✅ 여러 여정 시나리오 테스트 성공!")
        print(f"   - 첫 번째 여정 포인트: {points1}")
        print(f"   - 두 번째 여정 포인트: {points2}")
        print(f"   - 총 누적 포인트: {total_points}")
        print("=" * 60 + "\n")


class TestRejectionScenario:
    """여정 반려 시나리오 테스트"""

    @pytest.mark.asyncio
    async def test_trip_rejection_flow(
        self, authenticated_client: TestClient, admin_client: TestClient
    ):
        """
        여정 반려 플로우 테스트

        시나리오:
        1. 사용자가 여정 완료
        2. 관리자가 반려
        3. 사용자 포인트 변화 없음 확인
        4. 여정 상태 REJECTED 확인
        """
        # 이미지 데이터
        image_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01"
            b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )

        # 초기 포인트 확인
        initial_profile = authenticated_client.get("/api/v1/auth/profile")
        initial_points = initial_profile.json()["data"]["total_points"]

        # 여정 시작
        start_response = authenticated_client.post(
            "/api/v1/trips/start", json={"latitude": 35.8809, "longitude": 128.6286}
        )
        trip_id = start_response.json()["data"]["trip_id"]

        # 환승
        transfer_files = {"file": ("transfer.png", io.BytesIO(image_data), "image/png")}
        transfer_upload = authenticated_client.post(
            "/api/v1/storage/upload/transfer", files=transfer_files
        )
        transfer_image_url = transfer_upload.json()["data"]["url"]

        authenticated_client.post(
            f"/api/v1/trips/{trip_id}/transfer",
            json={
                "latitude": 35.8714,
                "longitude": 128.5988,
                "transfer_image_url": transfer_image_url,
            },
        )

        # 도착
        arrival_files = {"file": ("arrival.png", io.BytesIO(image_data), "image/png")}
        arrival_upload = authenticated_client.post(
            "/api/v1/storage/upload/arrival", files=arrival_files
        )
        arrival_image_url = arrival_upload.json()["data"]["url"]

        authenticated_client.post(
            f"/api/v1/trips/{trip_id}/arrival",
            json={
                "latitude": 35.8569,
                "longitude": 128.5932,
                "arrival_image_url": arrival_image_url,
            },
        )

        # 관리자가 반려
        reject_response = admin_client.post(
            f"/api/v1/admin/trips/{trip_id}/reject",
            json={"reason": "증빙 이미지가 불명확합니다"},
        )
        assert reject_response.status_code == 200
        assert reject_response.json()["data"]["status"] == "REJECTED"

        # 최종 검증
        final_profile = authenticated_client.get("/api/v1/auth/profile")
        final_points = final_profile.json()["data"]["total_points"]

        # 포인트 변화 없음
        assert final_points == initial_points

        # 여정 상태 확인
        trip_response = authenticated_client.get(f"/api/v1/trips/{trip_id}")
        trip_status = trip_response.json()["data"]["status"]
        assert trip_status == "REJECTED"

        print("\n" + "=" * 60)
        print("✅ 여정 반려 시나리오 테스트 성공!")
        print(f"   - 여정 ID: {trip_id}")
        print(f"   - 포인트 변화: {initial_points} → {final_points} (변화 없음)")
        print("=" * 60 + "\n")


class TestErrorRecoveryScenario:
    """에러 복구 시나리오 테스트"""

    @pytest.mark.asyncio
    async def test_duplicate_trip_prevention(self, authenticated_client: TestClient):
        """
        중복 여정 방지 테스트

        시나리오:
        1. 첫 번째 여정 시작
        2. 완료하지 않고 두 번째 여정 시작 시도
        3. 409 Conflict 에러 발생 확인
        """
        # 첫 번째 여정 시작
        start_data = {"latitude": 35.8809, "longitude": 128.6286}
        first_trip = authenticated_client.post("/api/v1/trips/start", json=start_data)
        assert first_trip.status_code == 201

        # 두 번째 여정 시작 시도 (진행 중인 여정이 있음)
        second_trip = authenticated_client.post("/api/v1/trips/start", json=start_data)
        assert second_trip.status_code == 409
        assert "진행 중" in second_trip.json()["message"]

        print("\n" + "=" * 60)
        print("✅ 중복 여정 방지 테스트 성공!")
        print("=" * 60 + "\n")
