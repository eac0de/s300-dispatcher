from typing import Literal

from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, Query, status

from api.dependencies.auth import EmployeeDep
from client.s300.models.tenant import TenantS300
from schemes.tenant_rating import TenantRatingRScheme
from services.tenant_rating_service import TenantRatingService

dispatcher_tenant_rating_router = APIRouter(
    tags=["dispatcher_tenant_rating"],
)


@dispatcher_tenant_rating_router.patch(
    path="/{tenant_id}/",
    status_code=status.HTTP_200_OK,
    response_model=TenantRatingRScheme,
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
    tenant_rating = await service.rate_tenant(rate)
    return TenantRatingRScheme(
        up=len(tenant_rating.up),
        down=len(tenant_rating.down),
        current_rate="up" if employee.id in tenant_rating.up else "down" if employee.id in tenant_rating.down else None,
    )


@dispatcher_tenant_rating_router.get(
    path="/{tenant_id}/",
    status_code=status.HTTP_200_OK,
    response_model=TenantRatingRScheme,
)
async def get_tenant_rating(
    employee: EmployeeDep,
    tenant_id: PydanticObjectId,
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
    tenant_rating = await service.get_tenant_rating()

    return TenantRatingRScheme(
        up=len(tenant_rating.up),
        down=len(tenant_rating.down),
        current_rate="up" if employee.id in tenant_rating.up else "down" if employee.id in tenant_rating.down else None,
    )
