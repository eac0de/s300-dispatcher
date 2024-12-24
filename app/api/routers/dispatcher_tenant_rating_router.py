from typing import Literal

from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, Query, status

from api.dependencies.auth import EmployeeDep
from client.s300.models.tenant import TenantS300
from schemes.tenant_stats import RatesTenantStats
from services.tenant_rating_service import TenantRatingService

dispatcher_tenant_rating_router = APIRouter(
    tags=["dispatcher_tenant_rating"],
)


@dispatcher_tenant_rating_router.post(
    path="/{tenant_id}/rate/",
    status_code=status.HTTP_200_OK,
    response_model=RatesTenantStats,
)
async def rate_tenant(
    employee: EmployeeDep,
    tenant_id: PydanticObjectId,
    rate: Literal["up", "down"] | None = Query(None),
):
    """
    Получения статистики по обращениям сотрудником.
    """
    tenant = await TenantS300.get(tenant_id)
    if not tenant:
        raise HTTPException(
            detail="Tenant not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    service = TenantRatingService(
        employee=employee,
        tenant=tenant,
    )
    result = await service.rate_tenant(rate)
    return result
