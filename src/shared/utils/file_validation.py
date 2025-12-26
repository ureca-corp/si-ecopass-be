"""
파일 검증 유틸리티

이미지 파일의 MIME 타입, 크기, 확장자 검증 기능 제공
"""

from fastapi import UploadFile

from src.shared.exceptions import ValidationError

# 허용되는 MIME 타입
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}

# 최대 파일 크기 (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024


def validate_image_file(file: UploadFile) -> None:
    """
    이미지 파일 유효성 검증
    MIME 타입과 파일 크기를 검증하고 실패 시 ValidationError 발생
    """
    # MIME 타입 검증
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise ValidationError(
            f"지원하지 않는 파일 형식입니다. "
            f"허용된 형식: {', '.join(ALLOWED_MIME_TYPES)} (현재: {file.content_type})"
        )

    # 파일 크기 검증 (file.size가 있는 경우에만 체크)
    if hasattr(file, "size") and file.size:
        if file.size > MAX_FILE_SIZE:
            max_mb = MAX_FILE_SIZE / (1024 * 1024)
            current_mb = file.size / (1024 * 1024)
            raise ValidationError(
                f"파일 크기가 너무 큽니다. "
                f"최대 {max_mb}MB 허용 (현재: {current_mb:.2f}MB)"
            )


def get_file_extension(filename: str) -> str:
    """
    파일명에서 확장자 추출
    확장자가 없는 경우 빈 문자열 반환
    """
    if "." in filename:
        return filename.rsplit(".", 1)[-1].lower()
    return ""
