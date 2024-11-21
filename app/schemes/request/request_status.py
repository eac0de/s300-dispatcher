"""
Модуль со схемами для обновления статуса и ресурсов заявки работником
"""

from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from models.request.constants import RequestStatus
from models.request.embs.resources import ManuallyAddedItemResourcesRS
from schemes.only_id import OnlyIdScheme


class ExecutionRequestDStatusUScheme(BaseModel):
    """
    Класс схемы модели выполнения для обновления статуса и ресурсов заявки работником
    """

    start_at: datetime | None = Field(
        title="Фактическое время начала выполнения заявки",
    )
    end_at: datetime | None = Field(
        title="Фактическое время окончания выполнения заявки",
    )
    provider: OnlyIdScheme = Field(
        title="Организация исполняющая заявку",
    )
    employees: list[OnlyIdScheme] = Field(
        title="Сотрудники исполняющие заявку",
    )
    description: str | None = Field(
        title="Описание выполненных работ",
    )
    is_partially: bool = Field(
        title="Выполнена частично",
    )
    delayed_until: datetime | None = Field(
        title="Время до которого перенесено выполнение заявки",
    )
    warranty_until: datetime | None = Field(
        title="Гарантия по",
    )


class ItemWarehouseResourcesRequestDStatusUScheme(BaseModel):
    """
    Класс схемы позиции склада для обновления статуса и ресурсов заявки работником
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор позиции со склада",
    )
    quantity: float = Field(
        gt=0,
        title="Количество позиции со склада",
    )


class WarehouseResourcesRequestDStatusUScheme(BaseModel):
    """
    Класс схемы склада для обновления статуса и ресурсов заявки работником
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор позиции со склада",
    )
    items: list[ItemWarehouseResourcesRequestDStatusUScheme] = Field(
        default=list,
        min_length=1,
        title="Позиции со склада",
    )


class ResourcesRequestDStatusUScheme(BaseModel):
    """
    Класс схемы ресурсов для обновления статуса и ресурсов заявки работником
    """

    materials: list[ManuallyAddedItemResourcesRS] = Field(
        title="Вручную добавленные материалы",
    )
    services: list[ManuallyAddedItemResourcesRS] = Field(
        title="Вручную добавленные услуги",
    )
    warehouses: list[WarehouseResourcesRequestDStatusUScheme] = Field(
        default_factory=list,
        title="Позиции со склада",
    )


class RequestDStatusUScheme(BaseModel):
    """
    Класс схемы заявки для обновления ее статуса и ресурсов работником
    """

    status: RequestStatus = Field(
        title="Статус заявки",
    )
    execution: ExecutionRequestDStatusUScheme = Field(
        title="Выполнение заявки",
    )
    resources: ResourcesRequestDStatusUScheme = Field(
        title="Ресурсы заявки",
    )
