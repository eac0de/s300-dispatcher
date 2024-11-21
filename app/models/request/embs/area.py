"""
Модуль с моделью квартиры заявки
"""

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class AreaRS(BaseModel):
    """
    Модель закешированного помещения
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор связанной заявки",
    )
    number: str = Field(
        title="Номер квартиры",
    )
    formatted_number: str = Field(
        title="Номер квартиры с приставкой и доп информацией",
    )
