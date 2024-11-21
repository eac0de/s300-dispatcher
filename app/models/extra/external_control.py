"""
Модуль с моделью внешнего управления
"""

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class ExternalControl(BaseModel):
    """
    Модель внешнего управления
    """

    id: PydanticObjectId = Field(  # type: ignore
        alias="_id",
        description="Идентификатор внешнего управления",
    )
    number: str = Field(
        title="Номер пользователя",
    )
    short_name: str = Field(
        title="Фамилия И.О. сотрудника",
    )
    full_name: str = Field(
        title="Фамилия Имя Отчество пользователя",
    )
    provider_id: PydanticObjectId = Field(
        title="Организация пользователя",
    )
