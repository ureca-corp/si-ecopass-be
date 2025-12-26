"""
EcoPass Repository Implementation (In-Memory for demo)

This is a concrete implementation of the repository interface.
In production, this would connect to Supabase.
"""

from typing import Optional
from uuid import UUID

from src.domain.entities.ecopass import EcoPass
from src.domain.repositories.ecopass_repository import IEcoPassRepository


class InMemoryEcoPassRepository(IEcoPassRepository):
    """
    In-memory implementation of EcoPass repository

    For demonstration purposes. Replace with SupabaseEcoPassRepository in production.
    """

    def __init__(self):
        self._storage: dict[UUID, EcoPass] = {}

    async def create(self, ecopass: EcoPass) -> EcoPass:
        """Create a new EcoPass"""
        self._storage[ecopass.id] = ecopass
        return ecopass

    async def get_by_id(self, ecopass_id: UUID) -> Optional[EcoPass]:
        """Get EcoPass by ID"""
        return self._storage.get(ecopass_id)

    async def get_by_user_id(self, user_id: str) -> list[EcoPass]:
        """Get all EcoPasses for a user"""
        return [ecopass for ecopass in self._storage.values() if ecopass.user_id == user_id]

    async def update(self, ecopass: EcoPass) -> EcoPass:
        """Update an existing EcoPass"""
        if ecopass.id not in self._storage:
            raise ValueError(f"EcoPass with id {ecopass.id} not found")
        self._storage[ecopass.id] = ecopass
        return ecopass

    async def delete(self, ecopass_id: UUID) -> bool:
        """Delete an EcoPass"""
        if ecopass_id in self._storage:
            del self._storage[ecopass_id]
            return True
        return False

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[EcoPass]:
        """List all EcoPasses with pagination"""
        all_items = list(self._storage.values())
        return all_items[skip : skip + limit]
