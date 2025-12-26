"""
EcoPass Dependencies

FastAPI dependency injection for EcoPass services
"""

from typing import Annotated, Optional

from fastapi import Depends

from src.application.services.ecopass_service import EcoPassService
from src.domain.repositories.ecopass_repository import IEcoPassRepository
from src.infrastructure.repositories.ecopass_repository_impl import InMemoryEcoPassRepository

# Singleton repository instance (in production, use proper DI container)
_repository: Optional[IEcoPassRepository] = None


def get_ecopass_repository() -> IEcoPassRepository:
    """Get EcoPass repository instance"""
    global _repository
    if _repository is None:
        _repository = InMemoryEcoPassRepository()
    return _repository


def get_ecopass_service(
    repository: Annotated[IEcoPassRepository, Depends(get_ecopass_repository)],
) -> EcoPassService:
    """Get EcoPass service instance"""
    return EcoPassService(repository=repository)
