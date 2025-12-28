"""
FastAPI 애플리케이션 진입점

미들웨어, 예외 핸들러, 라우터 설정을 포함한 메인 애플리케이션 구성
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.shared.exceptions import BaseAppException
from src.shared.schemas.response import ErrorResponse

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 생명주기 이벤트
    시작 시와 종료 시 실행되는 로직 정의
    """
    # 시작 시 실행
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📝 Environment: {settings.environment}")
    print(f"📚 API Documentation: http://{settings.host}:{settings.port}/docs")

    # SQLModel Database Engine 초기화
    if settings.database_url:
        from src.infrastructure.database.session import init_db
        init_db()
        print(f"✅ SQLModel Database Engine initialized")

    yield

    # 종료 시 실행
    if settings.database_url:
        from src.infrastructure.database.session import close_db
        close_db()
        print(f"🔒 SQLModel Database Engine closed")

    print(f"👋 Shutting down {settings.app_name}")


def create_application() -> FastAPI:
    """
    FastAPI 애플리케이션 생성 팩토리 함수
    앱 인스턴스, 미들웨어, 예외 핸들러, 라우터를 설정
    """

    app = FastAPI(
        title="SI-EcoPass Backend API",
        version=settings.app_version,
        swagger_ui_parameters={
            "persistAuthorization": True,  # 새로고침 시 토큰 유지
        },
        description="""
# SI-EcoPass Backend API

대구 지하철 환승 주차장 이용 장려 플랫폼의 백엔드 API입니다.

## 주요 기능

- 🔐 **사용자 인증**: 회원가입, 로그인, 프로필 관리
- 🚇 **역 조회**: 대구 지하철 역 및 주변 주차장 정보
- 🚗 **여정 관리**: 출발 → 환승 → 도착 3단계 프로세스
- 📷 **이미지 업로드**: Supabase Storage를 통한 인증 사진 저장
- 👮 **관리자**: 여정 승인/반려 및 포인트 지급

## 인증 방법

대부분의 API는 JWT Bearer Token 인증이 필요합니다:

1. `/api/v1/auth/login`으로 로그인
2. 응답에서 `access_token` 추출
3. 요청 헤더에 `Authorization: Bearer {access_token}` 추가

## 에러 코드

- `400 Bad Request`: 잘못된 요청 파라미터
- `401 Unauthorized`: 인증 토큰 없음 또는 만료
- `403 Forbidden`: 권한 없음 (관리자 전용 API 등)
- `404 Not Found`: 리소스를 찾을 수 없음
- `409 Conflict`: 리소스 충돌 (중복 이메일, 진행 중 여정 등)
- `422 Unprocessable Entity`: 유효성 검증 실패
- `500 Internal Server Error`: 서버 내부 오류

## 표준 응답 형식

모든 API는 다음 형식으로 응답합니다:

```json
{
  "status": "success" | "error",
  "message": "사람이 읽을 수 있는 메시지",
  "data": { ... } | null
}
```
        """,
        contact={
            "name": "SI-EcoPass Team",
            "email": "support@siecopass.com",
        },
        license_info={
            "name": "MIT License",
        },
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=[
            {
                "name": "Authentication",
                "description": "사용자 인증 및 프로필 관리 API",
            },
            {
                "name": "Stations",
                "description": "지하철 역 및 주차장 조회 API",
            },
            {
                "name": "Trips",
                "description": "여정 관리 API (출발, 환승, 도착)",
            },
            {
                "name": "Storage",
                "description": "이미지 업로드 및 저장 API",
            },
            {
                "name": "Admin",
                "description": "관리자 전용 API (승인, 반려)",
            },
            {
                "name": "Health",
                "description": "헬스체크 엔드포인트",
            },
        ],
        lifespan=lifespan,
    )

    # CORS 미들웨어 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list,
        allow_credentials=False,  # allow_origins=["*"]와 함께 사용하기 위해 False로 설정
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ============================================================
    # 예외 핸들러 (Exception Handlers)
    # ============================================================

    @app.exception_handler(BaseAppException)
    async def base_app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
        """
        커스텀 애플리케이션 예외 처리
        BaseAppException 계열의 모든 예외를 JSONResponse로 변환
        """
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse.create(message=exc.message).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Pydantic 유효성 검증 에러 처리
        Request Body 스키마 검증 실패 시 자동 호출
        """
        errors = exc.errors()
        error_messages = [f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in errors]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse.create(message=f"유효성 검증 실패: {'; '.join(error_messages)}").model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        예상치 못한 일반 예외 처리
        디버그 모드에서는 상세 에러 메시지를 반환
        """
        if settings.debug:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=ErrorResponse.create(message=f"서버 내부 오류: {str(exc)}").model_dump(),
            )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse.create(message="서버 내부 오류가 발생했습니다").model_dump(),
        )

    # ============================================================
    # 헬스 체크 엔드포인트
    # ============================================================

    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        서비스 상태 확인 엔드포인트
        로드 밸런서나 모니터링 시스템에서 사용
        """
        from src.shared.schemas.response import SuccessResponse

        return SuccessResponse.create(
            message="서비스가 정상 작동 중입니다",
            data={"status": "ok", "version": settings.app_version},
        )

    # ============================================================
    # 라우터 등록
    # ============================================================

    from src.api.routes.admin_routes import router as admin_router
    from src.api.routes.auth_routes import router as auth_router
    from src.api.routes.ecopass_routes import router as ecopass_router
    from src.api.routes.station_routes import router as station_router
    from src.api.routes.storage_routes import router as storage_router
    from src.api.routes.trip_routes import router as trip_router

    app.include_router(admin_router, prefix=settings.api_prefix)
    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(ecopass_router, prefix=settings.api_prefix)
    app.include_router(station_router, prefix=settings.api_prefix)
    app.include_router(storage_router, prefix=settings.api_prefix)
    app.include_router(trip_router, prefix=settings.api_prefix)

    return app


app = create_application()
