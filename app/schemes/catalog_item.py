"""
Модуль со схемами для создания и обновления позиций каталога
"""

from datetime import datetime

from beanie import PydanticObjectId
from pydantic import UUID4, BaseModel, Field

from models.catalog_item.catalog_item import CatalogItemPrice
from models.catalog_item.constants import CatalogItemGroup, CatalogMeasurementUnit
from schemes.only_id import OnlyIdScheme


class CatalogItemCScheme(BaseModel):
    """
    Основная схема для создания позиции каталога
    """

    name: str = Field(
        title="Название позиции",
    )
    description: str = Field(
        title="Описание позиции",
    )
    code: str = Field(
        title="Код позиции",
    )
    measurement_unit: CatalogMeasurementUnit = Field(
        title="Единица измерения позиции",
    )
    is_available: bool = Field(
        title="Доступна ли позиция",
    )
    is_divisible: bool = Field(
        title="Можно ли взять часть позиции",
    )
    available_from: datetime = Field(
        title="С какого времени доступна позиция",
    )
    available_until: datetime | None = Field(
        title="С какого времени доступна позиция",
    )
    group: CatalogItemGroup = Field(
        title="Группа позиции",
    )
    prices: list[CatalogItemPrice] = Field(
        title="Цены на позицию",
    )
    house_ids: set[PydanticObjectId] = Field(
        title="Идентификаторы домов к которым привязана позиция",
    )
    house_group_ids: set[PydanticObjectId] = Field(
        title="Идентификаторы групп домов к которым привязана позиция",
    )
    fias: set[UUID4] = Field(
        title="ФИАСы домов к которым привязана позиция",
    )


class CatalogItemUScheme(CatalogItemCScheme):
    """
    Основная схема для  обновления позиции каталога
    """

    image: OnlyIdScheme | None = Field(
        title="Изображение позиции",
    )
