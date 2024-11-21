"""
Модуль с дополнительным классом - домом, с которым связана заявка
"""

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class HouseRS(BaseModel):
    """
    Класс дома, с которым связана заявка. RS - Request Scheme
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор связанной заявки",
    )
    address: str = Field(
        title="Адрес дома",
    )
