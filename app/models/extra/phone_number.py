"""
Модуль с моделью номера телефона
"""

from enum import Enum

from pydantic import BaseModel, Field


class PhoneType(str, Enum):
    """
    Типы номеров телефонов
    """

    CELL = "cell"
    WORK = "work"
    DISPATCHER = "dispatcher"
    HOME = "home"
    FAX = "fax"
    EMERGENCY = "emergency"


class PhoneNumber(BaseModel):
    """
    Модель номера телефона
    """

    type: PhoneType = Field(
        alias="_type",
        default=PhoneType.CELL,
        title="Тип телефона",
    )
    number: str = Field(
        pattern=r"\d{10}",
        title="Полный номер телефона",
    )
    add: str | None = Field(
        default=None,
        pattern=r"\d*",
        title="Добавочный код телефона",
    )
