"""
커스텀 예외 클래스

도메인 특화 예외 처리를 위한 계층적 예외 구조
모든 예외는 BaseAppException을 상속하여 일관성 유지
"""

from typing import Any, Optional


class BaseAppException(Exception):
    """
    애플리케이션 모든 예외의 베이스 클래스
    message, status_code, details를 통일된 형태로 관리
    JSONResponse로 자동 변환되어 클라이언트에 반환
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(BaseAppException):
    """
    리소스를 찾을 수 없을 때 발생 (404)
    DB 조회 결과가 없거나 잘못된 ID 접근 시 사용
    """

    def __init__(self, message: str = "리소스를 찾을 수 없습니다", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, status_code=404, details=details)


class ValidationError(BaseAppException):
    """
    비즈니스 로직 검증 실패 시 발생 (422)
    Pydantic 검증과는 별도로 도메인 규칙 위반 시 사용
    """

    def __init__(self, message: str = "유효성 검증 실패", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, status_code=422, details=details)


class UnauthorizedError(BaseAppException):
    """
    인증되지 않은 접근 시도 시 발생 (401)
    로그인이 필요하거나 토큰이 유효하지 않을 때 사용
    """

    def __init__(self, message: str = "인증이 필요합니다", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, status_code=401, details=details)


class ForbiddenError(BaseAppException):
    """
    권한이 없는 리소스 접근 시 발생 (403)
    인증은 되었으나 해당 리소스에 대한 권한이 없을 때 사용
    """

    def __init__(self, message: str = "접근 권한이 없습니다", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, status_code=403, details=details)


class ConflictError(BaseAppException):
    """
    리소스 충돌 발생 시 사용 (409)
    중복된 데이터 생성 시도나 동시성 문제 발생 시 사용
    """

    def __init__(self, message: str = "리소스 충돌이 발생했습니다", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, status_code=409, details=details)


class InternalServerError(BaseAppException):
    """
    서버 내부 오류 발생 시 사용 (500)
    예상치 못한 예외나 시스템 오류 시 사용
    """

    def __init__(self, message: str = "서버 내부 오류가 발생했습니다", details: Optional[dict[str, Any]] = None):
        super().__init__(message=message, status_code=500, details=details)
