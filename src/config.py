"""
애플리케이션 설정

pydantic-settings를 사용한 환경 변수 기반 설정 관리
.env 파일에서 설정을 로드하고 타입 검증 제공
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    환경 변수에서 로드되는 애플리케이션 설정
    .env 파일 또는 시스템 환경 변수에서 값을 읽어옴
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 애플리케이션 기본 정보
    app_name: str = Field(default="SI-EcoPass Backend", description="애플리케이션 이름")
    app_version: str = Field(default="0.1.0", description="애플리케이션 버전")
    debug: bool = Field(default=False, description="디버그 모드 활성화 여부")
    environment: str = Field(default="development", description="실행 환경 (development/production)")

    # API 설정
    api_prefix: str = Field(default="/api/v1", description="API 경로 접두사")
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="CORS 허용 오리진 (쉼표로 구분)",
    )

    @property
    def origins_list(self) -> list[str]:
        """
        쉼표로 구분된 allowed_origins 문자열을 리스트로 변환
        CORS 미들웨어 설정에 사용
        """
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    # Supabase 연결 정보
    supabase_url: str = Field(..., description="Supabase 프로젝트 URL")
    supabase_key: str = Field(..., description="Supabase anon/service 키")

    # Database 연결 정보 (SQLModel용)
    database_url: str = Field(
        ...,
        description="PostgreSQL 연결 URL (SQLModel용, 비밀번호의 @ 문자는 %40으로 인코딩)",
    )

    # 네이버 클라우드 Maps API (Geocoding)
    naver_client_id: str = Field(..., description="네이버 클라우드 플랫폼 Client ID")
    naver_client_secret: str = Field(..., description="네이버 클라우드 플랫폼 Client Secret")

    # Uvicorn 서버 설정
    host: str = Field(default="0.0.0.0", description="서버 바인딩 호스트")
    port: int = Field(default=8000, description="서버 바인딩 포트")


@lru_cache
def get_settings() -> Settings:
    """
    캐시된 설정 인스턴스 반환 (싱글톤)
    동일한 설정 객체를 재사용하여 성능 최적화
    """
    return Settings()
