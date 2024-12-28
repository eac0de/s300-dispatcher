"""
Модуль со схемами для обновления статуса и ресурсов заявки работником
"""

from datetime import datetime
from typing import Literal

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from models.request.constants import RequestStatus
from models.request.embs.resources import ManuallyAddedItemResourcesRS
from schemes.extra.only_id import OnlyIdScheme


class ExecutionRequestDStatusUScheme(BaseModel):
    """
    Класс схемы модели выполнения для обновления статуса и ресурсов заявки работником
    """

    start_at: datetime | None = Field(
        default=None,
        title="Фактическое время начала выполнения заявки",
    )
    end_at: datetime | None = Field(
        default=None,
        title="Фактическое время окончания выполнения заявки",
    )
    provider: OnlyIdScheme | None = Field(
        default=None,
        title="Организация исполняющая заявку",
    )
    employees: list[OnlyIdScheme] | None = Field(
        default=None,
        title="Сотрудники исполняющие заявку",
    )
    description: str | None = Field(
        default=None,
        title="Описание выполненных работ",
    )
    is_partially: bool | None = Field(
        default=None,
        title="Выполнена частично",
    )
    delayed_until: datetime | None = Field(
        default=None,
        title="Время до которого перенесено выполнение заявки",
    )
    warranty_until: datetime | None = Field(
        default=None,
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
        default_factory=list,
        min_length=1,
        title="Позиции со склада",
    )


class ResourcesRequestDStatusUScheme(BaseModel):
    """
    Класс схемы ресурсов для обновления статуса и ресурсов заявки работником
    """

    materials: list[ManuallyAddedItemResourcesRS] | None = Field(
        default=None,
        title="Вручную добавленные материалы",
    )
    services: list[ManuallyAddedItemResourcesRS] | None = Field(
        default=None,
        title="Вручную добавленные услуги",
    )
    warehouses: list[WarehouseResourcesRequestDStatusUScheme] | None = Field(
        default=None,
        title="Позиции со склада",
    )


class RequestDStatusUScheme(BaseModel):
    """
    Класс схемы заявки для обновления ее статуса и ресурсов работником
    """

    status: Literal[RequestStatus.ABANDONMENT, RequestStatus.DELAYED, RequestStatus.HIDDEN, RequestStatus.PERFORMED, RequestStatus.REFUSAL, RequestStatus.RUN] | None = Field(
        default=None,
        title="Статус заявки",
    )
    execution: ExecutionRequestDStatusUScheme | None = Field(
        default=None,
        title="Выполнение заявки",
    )
    resources: ResourcesRequestDStatusUScheme | None = Field(
        default=None,
        title="Ресурсы заявки",
    )
