"""
Admin Service Dependencies

AdminService를 위한 FastAPI 의존성 주입 함수
TripRepository와 AuthService를 조합하여 AdminService 생성
"""

from fastapi import Depends
from supabase import Client

from src.application.services.admin_service import AdminService
from src.application.services.auth_service import AuthService
from src.domain.repositories.trip_repository import ITripRepository
from src.infrastructure.database.supabase import get_db
from src.infrastructure.repositories.trip_repository_impl import SupbaseTripRepository

from .auth_deps import get_auth_service


def get_trip_repository(db: Client = Depends(get_db)) -> ITripRepository:
    """
    TripRepository 의존성 주입
    Supabase 기반 구현체 반환
    """
    return SupbaseTripRepository(db)


def get_admin_service(
    trip_repository: ITripRepository = Depends(get_trip_repository),
    auth_service: AuthService = Depends(get_auth_service),
) -> AdminService:
    """
    AdminService 의존성 주입
    FastAPI 엔드포인트에서 AdminService를 사용할 수 있도록 제공
    """
    return AdminService(trip_repository=trip_repository, auth_service=auth_service)
