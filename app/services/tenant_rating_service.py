"""
Модуль с сервисом для работы с шаблонами заявок
"""

from typing import Literal

from client.s300.models.employee import EmployeeS300
from client.s300.models.tenant import TenantS300
from models.tenant_rating.tenant_rating import TenantRating


class TenantRatingService:
    """
    Сервис для работы с шаблонами заявок
    """

    def __init__(
        self,
        employee: EmployeeS300,
        tenant: TenantS300,
    ):
        """
        Инициализация сервиса

        Args:
            employee (EmployeeS300): Сотрудник который работает с шаблонами заявок
        """
        self.employee = employee
        self.tenant = tenant

    async def rate_tenant(
        self,
        rate: Literal["up", "down"] | None,
    ) -> TenantRating:
        tenant_rating = await self.get_tenant_rating()
        if rate == "up":
            tenant_rating.up.add(self.employee.id)
            tenant_rating.down.discard(self.employee.id)
        elif rate == "down":
            tenant_rating.down.add(self.employee.id)
            tenant_rating.up.discard(self.employee.id)
        else:
            tenant_rating.up.discard(self.employee.id)
            tenant_rating.down.discard(self.employee.id)
        return await tenant_rating.save()

    async def get_tenant_rating(self) -> TenantRating:
        tenant_rating = await TenantRating.find_one({"tenant_id": self.tenant.id, "provider_id": self.employee.provider.id})
        if not tenant_rating:
            tenant_rating = TenantRating(
                tenant_id=self.tenant.id,
                provider_id=self.employee.provider.id,
            )
        return tenant_rating
