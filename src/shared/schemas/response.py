"""
표준화된 API 응답 스키마

모든 API 응답은 아래 형식을 따름:
{
    "status": "success" | "error",
    "message": "설명 메시지",
    "data": {...} | null
}
"""

from typing import Generic, Literal, Optional, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class BaseResponse(BaseModel, Generic[DataT]):
    """
    모든 API 엔드포인트의 베이스 응답 모델
    제네릭 타입 DataT를 통해 다양한 data 타입 지원
    """

    status: Literal["success", "error"] = Field(
        ...,
        description="응답 상태 (성공/실패)",
        examples=["success"],
    )
    message: str = Field(
        ...,
        description="사람이 읽을 수 있는 응답 메시지",
        examples=["작업이 성공적으로 완료되었습니다"],
    )
    data: Optional[DataT] = Field(
        None,
        description="응답 데이터 페이로드",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "작업이 성공적으로 완료되었습니다",
                "data": {},
            }
        }


class SuccessResponse(BaseResponse[DataT], Generic[DataT]):
    """
    성공 응답 모델
    status가 항상 "success"로 고정됨
    """

    status: Literal["success"] = "success"

    @classmethod
    def create(cls, message: str, data: Optional[DataT] = None) -> "SuccessResponse[DataT]":
        """
        성공 응답 생성 팩토리 메서드
        일관된 응답 생성을 보장
        """
        return cls(status="success", message=message, data=data)


class SuccessResponseNoData(BaseModel):
    """
    데이터 없는 성공 응답 모델
    DELETE 등 응답 본문이 필요 없는 엔드포인트에서 사용
    """

    status: Literal["success"] = "success"
    message: str = Field(
        ...,
        description="사람이 읽을 수 있는 응답 메시지",
        examples=["삭제가 완료되었습니다"],
    )

    @classmethod
    def create(cls, message: str) -> "SuccessResponseNoData":
        """
        데이터 없는 성공 응답 생성 팩토리 메서드
        """
        return cls(status="success", message=message)


class ErrorResponse(BaseResponse[None]):
    """
    에러 응답 모델
    status가 항상 "error"로 고정되고 data는 항상 null
    """

    status: Literal["error"] = "error"
    data: None = None

    @classmethod
    def create(cls, message: str) -> "ErrorResponse":
        """
        에러 응답 생성 팩토리 메서드
        예외 핸들러에서 사용
        """
        return cls(status="error", message=message, data=None)


class PaginationMetadata(BaseModel):
    """
    페이지네이션 메타데이터
    리스트 응답 시 페이지 정보 제공
    """

    page: int = Field(..., description="현재 페이지 번호", ge=1)
    page_size: int = Field(..., description="페이지당 아이템 수", ge=1, le=100)
    total_items: int = Field(..., description="전체 아이템 수", ge=0)
    total_pages: int = Field(..., description="전체 페이지 수", ge=0)


class PaginatedData(BaseModel, Generic[DataT]):
    """
    페이지네이션된 데이터 래퍼
    items와 pagination을 함께 반환
    """

    items: list[DataT] = Field(..., description="현재 페이지의 아이템 리스트")
    pagination: PaginationMetadata = Field(..., description="페이지네이션 메타데이터")
