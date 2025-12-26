"""
EcoPass Application Service

Orchestrates business operations and coordinates between domain and infrastructure layers
"""

from typing import Optional
from uuid import UUID

from src.domain.entities.ecopass import EcoPass
from src.domain.repositories.ecopass_repository import IEcoPassRepository
from src.shared.exceptions import NotFoundError


class EcoPassService:
    """
    EcoPass Application Service

    Implements use cases and business logic for EcoPass management
    """

    def __init__(self, repository: IEcoPassRepository):
        self.repository = repository

    async def create_ecopass(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
    ) -> EcoPass:
        """Create a new EcoPass"""
        ecopass = EcoPass(
            user_id=user_id,
            title=title,
            description=description,
        )
        return await self.repository.create(ecopass)

    async def get_ecopass(self, ecopass_id: UUID) -> EcoPass:
        """Get an EcoPass by ID"""
        ecopass = await self.repository.get_by_id(ecopass_id)
        if not ecopass:
            raise NotFoundError(f"EcoPass with id {ecopass_id} not found")
        return ecopass

    async def get_user_ecopasses(self, user_id: str) -> list[EcoPass]:
        """Get all EcoPasses for a user"""
        return await self.repository.get_by_user_id(user_id)

    async def add_points_to_ecopass(self, ecopass_id: UUID, points: int) -> EcoPass:
        """Add points to an EcoPass"""
        ecopass = await self.get_ecopass(ecopass_id)
        ecopass.add_points(points)
        return await self.repository.update(ecopass)

    async def deactivate_ecopass(self, ecopass_id: UUID) -> EcoPass:
        """Deactivate an EcoPass"""
        ecopass = await self.get_ecopass(ecopass_id)
        ecopass.deactivate()
        return await self.repository.update(ecopass)

    async def list_ecopasses(self, skip: int = 0, limit: int = 100) -> list[EcoPass]:
        """List all EcoPasses with pagination"""
        return await self.repository.list_all(skip=skip, limit=limit)

    async def delete_ecopass(self, ecopass_id: UUID) -> bool:
        """Delete an EcoPass"""
        # Verify it exists first
        await self.get_ecopass(ecopass_id)
        return await self.repository.delete(ecopass_id)
