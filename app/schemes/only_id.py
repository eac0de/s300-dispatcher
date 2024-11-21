"""
Модуль с дополнительной схемой модели только с id
"""

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class OnlyIdScheme(BaseModel):
    """
    Класс схемы модели только с id
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор",
    )
