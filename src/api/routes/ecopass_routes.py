"""
EcoPass API Routes

RESTful endpoints for EcoPass management
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies.ecopass_deps import get_ecopass_service
from src.api.schemas.ecopass_schemas import (
    AddPointsRequest,
    CreateEcoPassRequest,
    EcoPassListResponse,
    EcoPassResponse,
)
from src.application.services.ecopass_service import EcoPassService
from src.shared.schemas.response import SuccessResponse, SuccessResponseNoData

router = APIRouter(prefix="/ecopasses", tags=["EcoPasses"])


@router.post(
    "",
    response_model=SuccessResponse[EcoPassResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new EcoPass",
    description="Create a new EcoPass for a user",
)
async def create_ecopass(
    request: CreateEcoPassRequest,
    service: Annotated[EcoPassService, Depends(get_ecopass_service)],
):
    """Create a new EcoPass"""
    ecopass = await service.create_ecopass(
        user_id=request.user_id,
        title=request.title,
        description=request.description,
    )
    return SuccessResponse.create(
        message="EcoPass created successfully",
        data=EcoPassResponse.model_validate(ecopass),
    )


@router.get(
    "/{ecopass_id}",
    response_model=SuccessResponse[EcoPassResponse],
    summary="Get an EcoPass by ID",
    description="Retrieve a specific EcoPass by its unique identifier",
)
async def get_ecopass(
    ecopass_id: UUID,
    service: Annotated[EcoPassService, Depends(get_ecopass_service)],
):
    """Get an EcoPass by ID"""
    ecopass = await service.get_ecopass(ecopass_id)
    return SuccessResponse.create(
        message="EcoPass retrieved successfully",
        data=EcoPassResponse.model_validate(ecopass),
    )


@router.get(
    "/user/{user_id}",
    response_model=SuccessResponse[EcoPassListResponse],
    summary="Get all EcoPasses for a user",
    description="Retrieve all EcoPasses owned by a specific user",
)
async def get_user_ecopasses(
    user_id: str,
    service: Annotated[EcoPassService, Depends(get_ecopass_service)],
):
    """Get all EcoPasses for a user"""
    ecopasses = await service.get_user_ecopasses(user_id)
    return SuccessResponse.create(
        message=f"Found {len(ecopasses)} EcoPass(es) for user {user_id}",
        data=EcoPassListResponse(
            items=[EcoPassResponse.model_validate(ep) for ep in ecopasses],
            total=len(ecopasses),
        ),
    )


@router.get(
    "",
    response_model=SuccessResponse[EcoPassListResponse],
    summary="List all EcoPasses",
    description="List all EcoPasses with pagination support",
)
async def list_ecopasses(
    service: Annotated[EcoPassService, Depends(get_ecopass_service)],
    skip: Annotated[int, Query(ge=0, description="Number of items to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum number of items to return")] = 100,
):
    """List all EcoPasses with pagination"""
    ecopasses = await service.list_ecopasses(skip=skip, limit=limit)
    return SuccessResponse.create(
        message=f"Retrieved {len(ecopasses)} EcoPass(es)",
        data=EcoPassListResponse(
            items=[EcoPassResponse.model_validate(ep) for ep in ecopasses],
            total=len(ecopasses),
        ),
    )


@router.post(
    "/{ecopass_id}/points",
    response_model=SuccessResponse[EcoPassResponse],
    summary="Add points to an EcoPass",
    description="Add environmental points to an existing EcoPass",
)
async def add_points(
    ecopass_id: UUID,
    request: AddPointsRequest,
    service: Annotated[EcoPassService, Depends(get_ecopass_service)],
):
    """Add points to an EcoPass"""
    ecopass = await service.add_points_to_ecopass(ecopass_id, request.points)
    return SuccessResponse.create(
        message=f"Added {request.points} points successfully",
        data=EcoPassResponse.model_validate(ecopass),
    )


@router.post(
    "/{ecopass_id}/deactivate",
    response_model=SuccessResponse[EcoPassResponse],
    summary="Deactivate an EcoPass",
    description="Deactivate an existing EcoPass",
)
async def deactivate_ecopass(
    ecopass_id: UUID,
    service: Annotated[EcoPassService, Depends(get_ecopass_service)],
):
    """Deactivate an EcoPass"""
    ecopass = await service.deactivate_ecopass(ecopass_id)
    return SuccessResponse.create(
        message="EcoPass deactivated successfully",
        data=EcoPassResponse.model_validate(ecopass),
    )


@router.delete(
    "/{ecopass_id}",
    response_model=SuccessResponseNoData,
    status_code=status.HTTP_200_OK,
    summary="Delete an EcoPass",
    description="Permanently delete an EcoPass",
)
async def delete_ecopass(
    ecopass_id: UUID,
    service: Annotated[EcoPassService, Depends(get_ecopass_service)],
):
    """Delete an EcoPass"""
    await service.delete_ecopass(ecopass_id)
    return SuccessResponseNoData.create(
        message="EcoPass deleted successfully",
    )
