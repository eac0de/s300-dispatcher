"""
Модуль с классом истории изменения заявки
"""

from datetime import datetime
from typing import Any

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from pymongo import IndexModel

from models.request_history.constants import UpdateUserType


class UpdatedField(BaseModel):
    """
    Класс измененного поля заявки
    """

    name: str = Field(
        title="Название измененного поля",
    )
    value: Any = Field(
        title="Значение измененного поля",
    )
    name_display: str = Field(
        title="Название поля для отображения на фронтенде",
    )
    value_display: str = Field(
        title="Значение для отображения на фронтенде",
    )
    link: str | None = Field(
        default=None,
        title="Ссылка для получения файла",
    )


class UpdateUser(BaseModel):
    """
    Класс пользователя изменившего заявку
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор пользователя",
    )
    full_name: str = Field(
        title="Фамилия Имя Отчество пользователя",
    )
    type: UpdateUserType = Field(
        title="Тип пользователя",
        alias="_type",
    )


class Update(BaseModel):
    """
    Класс изменения заявки
    """

    user: UpdateUser = Field(
        title="Пользователь изменивший заявку",
    )
    updated_fields: list[UpdatedField] = Field(
        title="Изменения",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        title="Значение для отображения на фронтенде, если None то отображать не нужно",
    )
    tag: str | None = Field(
        default=None,
        title="Тег для различия видов обновления",
    )


class RequestHistory(Document):
    """
    Класс истории изменения заявки
    """

    id: PydanticObjectId = Field(
        default_factory=PydanticObjectId,
        alias="_id",
        description="MongoDB document ObjectID",
    )
    request_id: PydanticObjectId = Field(
        title="Идентификатор заявки",
    )
    updates: list[Update] = Field(
        default_factory=list,
        title="Изменения",
    )

    class Settings:
        """
        Класс настроек истории изменения заявки
        """

        indexes = [
            IndexModel(
                keys=[("request_id")],
                name="request_id__idx",
                unique=True,
            ),
        ]
