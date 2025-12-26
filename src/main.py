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
    yield
    # 종료 시 실행
    print(f"👋 Shutting down {settings.app_name}")


def create_application() -> FastAPI:
    """
    FastAPI 애플리케이션 생성 팩토리 함수
    앱 인스턴스, 미들웨어, 예외 핸들러, 라우터를 설정
    """

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="SI-EcoPass Backend API - DDD 아키텍처 기반",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS 미들웨어 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list,
        allow_credentials=True,
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

    from src.api.routes.ecopass_routes import router as ecopass_router

    app.include_router(ecopass_router, prefix=settings.api_prefix)

    return app


app = create_application()
