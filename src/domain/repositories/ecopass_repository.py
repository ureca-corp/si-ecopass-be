"""
EcoPass Repository Interface

Defines the contract for EcoPass data persistence (following Repository Pattern)
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.domain.entities.ecopass import EcoPass


class IEcoPassRepository(ABC):
    """
    EcoPass Repository Interface

    This is a domain interface - the actual implementation belongs in infrastructure layer
    """

    @abstractmethod
    async def create(self, ecopass: EcoPass) -> EcoPass:
        """Create a new EcoPass"""
        pass

    @abstractmethod
    async def get_by_id(self, ecopass_id: UUID) -> Optional[EcoPass]:
        """Get EcoPass by ID"""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> list[EcoPass]:
        """Get all EcoPasses for a user"""
        pass

    @abstractmethod
    async def update(self, ecopass: EcoPass) -> EcoPass:
        """Update an existing EcoPass"""
        pass

    @abstractmethod
    async def delete(self, ecopass_id: UUID) -> bool:
        """Delete an EcoPass"""
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[EcoPass]:
        """List all EcoPasses with pagination"""
        pass
