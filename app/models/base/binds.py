"""
Модуль с моделями привязок
"""

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class ProviderHouseGroupBinds(BaseModel):
    """
    Модель привязки к провайдерам и группам домов
    """

    pr: set[PydanticObjectId] = Field(
        default_factory=set,
        title="Привязка к организации",
    )
    hg: set[PydanticObjectId] = Field(
        default_factory=set,
        title="Привязка к группе домов",
    )


class ProviderBinds(BaseModel):
    """
    Модель привязки к провайдерам
    """

    pr: set[PydanticObjectId] = Field(
        default_factory=set,
        title="Привязка к организации",
    )
