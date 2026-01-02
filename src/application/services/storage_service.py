"""
Storage Application Service

Supabase Storage를 활용한 이미지 업로드/관리 서비스
여행 인증 이미지 저장 및 URL 반환 기능 제공
"""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import UploadFile
from supabase import Client

from src.shared.exceptions import NotFoundError, UnauthorizedError, ValidationError
from src.shared.utils.file_validation import validate_image_file


class StorageService:
    """
    스토리지 서비스
    이미지 업로드, 삭제, URL 반환 등의 유스케이스 구현
    """

    STORAGE_BUCKET = "trips"  # Supabase Storage 버킷명
    ALLOWED_STAGES = {"transfer", "arrival"}  # 허용된 단계

    def __init__(self, db: Client):
        """
        StorageService 초기화
        Supabase 클라이언트를 의존성으로 주입받음
        """
        self.db = db
        self.storage = db.storage.from_(self.STORAGE_BUCKET)

    async def upload_image(
        self,
        user_id: UUID,
        image_file: UploadFile,
        stage: str,
    ) -> str:
        """
        이미지 업로드 (trip_id 없이)
        1. 파일 유효성 검증 (형식, 크기)
        2. 단계(stage) 검증
        3. 이미지 업로드
        4. 공개 URL 반환
        """
        # 1. 파일 유효성 검증
        validate_image_file(image_file)

        # 2. 단계(stage) 검증
        if stage not in self.ALLOWED_STAGES:
            raise ValidationError(
                f"올바르지 않은 단계입니다. "
                f"허용된 값: {', '.join(self.ALLOWED_STAGES)} (현재: {stage})"
            )

        # 3. 파일 경로 구성: {user_id}_{timestamp}_{stage}.jpg
        from datetime import datetime
        from uuid import uuid4
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid4())[:8]  # 고유성 보장 (마이크로초 단위 업로드 지원)
        file_path = f"{user_id}/{timestamp}_{unique_id}_{stage}.jpg"

        # 4. 이미지 업로드
        file_bytes = await image_file.read()

        try:
            self.storage.upload(
                path=file_path,
                file=file_bytes,
                file_options={"content-type": "image/jpeg"},
            )
        except Exception as e:
            raise ValidationError(f"이미지 업로드에 실패했습니다: {str(e)}")

        # 5. Public URL 반환 (영구 유효, 만료 없음)
        public_url = self.storage.get_public_url(file_path)
        return public_url

    async def upload_trip_image(
        self,
        trip_id: UUID,
        user_id: UUID,
        image_file: UploadFile,
        stage: str,
    ) -> str:
        """
        여행 인증 이미지 업로드
        1. 파일 유효성 검증 (형식, 크기)
        2. 단계(stage) 검증
        3. 여행 소유권 검증
        4. 기존 이미지 삭제 (있는 경우)
        5. 새 이미지 업로드
        6. 공개 URL 반환
        """
        # 1. 파일 유효성 검증
        validate_image_file(image_file)

        # 2. 단계(stage) 검증
        if stage not in self.ALLOWED_STAGES:
            raise ValidationError(
                f"올바르지 않은 단계입니다. "
                f"허용된 값: {', '.join(self.ALLOWED_STAGES)} (현재: {stage})"
            )

        # 3. 여행 소유권 검증 (trips 테이블 조회)
        trip_response = self.db.table("trips").select("user_id").eq("id", str(trip_id)).execute()

        if not trip_response.data:
            raise NotFoundError(f"여행을 찾을 수 없습니다 (ID: {trip_id})")

        trip_owner_id = trip_response.data[0]["user_id"]
        if str(trip_owner_id) != str(user_id):
            raise UnauthorizedError("본인의 여행에만 이미지를 업로드할 수 있습니다")

        # 4. 파일 경로 구성: {trip_id}/{stage}.jpg
        file_path = f"{trip_id}/{stage}.jpg"

        # 5. 기존 이미지 삭제 (있는 경우, 에러 무시)
        try:
            self.storage.remove([file_path])
        except Exception:
            # 파일이 없거나 삭제 실패 시 무시하고 계속 진행
            pass

        # 6. 파일 읽기 (한 번만 읽음)
        file_bytes = await image_file.read()

        # 7. Supabase Storage에 업로드
        try:
            self.storage.upload(
                path=file_path,
                file=file_bytes,
                file_options={"content-type": image_file.content_type},
            )
        except Exception as e:
            raise ValidationError(f"이미지 업로드 실패: {str(e)}")

        # 8. Public URL 반환 (영구 유효, 만료 없음)
        public_url = self.storage.get_public_url(file_path)

        return public_url

    def get_upload_timestamp(self) -> datetime:
        """
        업로드 타임스탬프 반환
        응답 스키마에서 uploaded_at 필드로 사용
        """
        return datetime.now(timezone.utc)
