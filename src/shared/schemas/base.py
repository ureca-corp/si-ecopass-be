"""
표준 Request/Response 베이스 클래스

모든 API 요청/응답 스키마의 기반이 되는 추상 클래스
"""

from pydantic import BaseModel, ConfigDict


class BaseRequest(BaseModel):
    """
    모든 Request 스키마의 베이스 클래스
    ~~Request 명명 규칙을 따르는 클래스에서 상속
    """

    model_config = ConfigDict(
        # 추가 필드를 허용하지 않아 API 계약을 엄격하게 유지
        extra="forbid",
        # strict 모드: 타입 강제 변환 없이 정확한 타입만 허용
        strict=False,
        # JSON 스키마 생성 시 사용
        use_enum_values=True,
    )


class BaseResponse(BaseModel):
    """
    모든 Response 스키마의 베이스 클래스
    ~~Response 명명 규칙을 따르는 클래스에서 상속
    """

    model_config = ConfigDict(
        # SQLModel 엔티티를 직접 Response로 변환 가능
        from_attributes=True,
        # 응답 시에는 추가 필드 허용 (유연성)
        extra="ignore",
        # datetime 등의 복잡한 타입을 JSON 직렬화 가능하게 설정
        json_encoders={},
        # 타임존이 있는 datetime을 ISO 8601 문자열로 직렬화
        ser_json_timedelta="iso8601",
    )
