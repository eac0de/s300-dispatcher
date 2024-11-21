"""
Модуль со схемами отображения графика работы работников
"""

from datetime import datetime

from pydantic import BaseModel, Field

from models.request_history.request_history import UpdateUser


class UpdatedFieldUpdateRequestHistoryRScheme(BaseModel):
    """
    Класс схемы обновленного поля для отображения его работнику
    """

    name_display: str = Field(
        title="Название поля для отображения на фронтенде",
    )
    value_display: str = Field(
        title="Значение для отображения на фронтенде",
    )
    link: str | None = Field(
        title="Ссылка для получения файла или чего-нибудь другого)",
    )


class UpdateRequestHistoryRScheme(BaseModel):
    """
    Класс схемы обновления для отображения его работнику
    """

    user: UpdateUser | None = Field(
        title="Пользователь",
    )
    updated_fields: list[UpdatedFieldUpdateRequestHistoryRScheme] = Field(
        title="Изменения",
    )
    updated_at: datetime = Field(
        title="Значение для отображения на FE, если None то отображать не нужно",
    )
