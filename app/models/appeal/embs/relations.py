"""
Модуль с дополнительным классом - связей заявки с другими классами или другими заявками
"""

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class RequestRelationsAS(BaseModel):
    """
    Класс связанной заявки
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор связанной заявки",
    )
    number: str = Field(
        title="Номер связанной заявки",
    )


class RelationsAS(BaseModel):
    """
    Класс связей обращения с другими классами или другими обращениями
    """

    request: RequestRelationsAS | None = Field(
        default=None,
        title="Связанная заявка",
    )
