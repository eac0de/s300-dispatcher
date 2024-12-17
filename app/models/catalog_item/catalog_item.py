"""
Модуль с моделью позиции каталога 
"""

from datetime import datetime

from beanie import PydanticObjectId
from file_manager import File
from pydantic import BaseModel, Field
from pymongo import IndexModel

from models.base_document import BaseDocument
from models.catalog_item.constants import CatalogItemGroup, CatalogMeasurementUnit


class CatalogItemPrice(BaseModel):
    """
    Модель цены или ндс позиции каталога
    """

    start_at: datetime = Field(
        title="Время с которого действует цена",
    )
    amount: int = Field(
        ge=100,
        title="Цена",
    )


class CatalogItem(BaseDocument):
    """
    Модель позиции каталога
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
        default=True,
        title="Доступна ли позиция",
    )
    is_divisible: bool = Field(
        default=False,
        title="Можно ли взять часть позиции",
    )
    available_from: datetime = Field(
        title="С какого времени доступна позиция",
    )
    available_until: datetime | None = Field(
        default=None,
        title="С какого времени доступна позиция",
    )
    image: File | None = Field(
        default=None,
        title="Изображение позиции",
    )
    group: CatalogItemGroup = Field(
        title="Группа позиции",
    )
    provider_id: PydanticObjectId = Field(
        title="Идентификатор организации",
    )
    prices: list[CatalogItemPrice] = Field(
        default_factory=list,
        title="Цены на позицию",
    )
    house_ids: set[PydanticObjectId] = Field(
        title="Идентификаторы домов к которым привязана позиция",
    )

    class Settings:
        """
        Настройки модели позиции каталога
        """

        keep_nulls = False
        indexes = [
            IndexModel(
                keys=["provider_id", "name"],
                name="provider_id__name__idx",
                unique=True,
            ),
            IndexModel(
                keys=["provider_id", "code"],
                name="provider_id__code__idx",
                unique=True,
            ),
        ]
