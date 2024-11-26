"""
Модуль дополнительного класса заявки - ресурсы
"""

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class ItemWarehouseResourcesRS(BaseModel):
    """
    Класс позиции склада
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор позиции со склада",
    )
    name: str = Field(
        title="Название позиции со склада",
    )
    price: int = Field(
        ge=100,
        title="Цена, установленная за единицу позиции со склада",
    )
    quantity: float = Field(
        gt=0,
        title="Количество позиции со склада",
    )


class WarehouseResourcesRS(BaseModel):
    """
    Класс склада
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор склада",
    )
    name: str = Field(
        title="Название склада",
    )
    items: list[ItemWarehouseResourcesRS] = Field(
        default_factory=list,
        min_length=1,
        title="Позиции со склада",
    )


class ManuallyAddedItemResourcesRS(BaseModel):
    """
    Класс вручную добавленной позиции
    """

    name: str = Field(
        title="Название материала/услуги",
    )
    price: int = Field(
        ge=100,
        title="Цена, установленная за единицу материала/услугу",
    )
    quantity: float = Field(
        gt=0,
        title="Количество материалов/услуг",
    )


class ResourcesRS(BaseModel):
    """
    Класс ресурсов Заявки
    """

    materials: list[ManuallyAddedItemResourcesRS] = Field(
        default_factory=list,
        title="Вручную добавленные материалы",
    )
    services: list[ManuallyAddedItemResourcesRS] = Field(
        default_factory=list,
        title="Вручную добавленные услуги",
    )
    warehouses: list[WarehouseResourcesRS] = Field(
        default_factory=list,
        title="Позиции со склада",
    )
