"""
Модуль с классом архивированной заявки
"""

from datetime import datetime
from enum import Enum

from beanie import PydanticObjectId
from pydantic import Field

from models.request.request import RequestModel


class ArchiverType(str, Enum):
    """
    Типы того, кто заархивировал заявку
    """

    EMPLOYEE = "employee"
    SYSTEM = "system"


class ArchivedRequestModel(RequestModel):
    """
    Класс заархивированной заявки
    """

    archived_at: datetime = Field(
        default_factory=datetime.now,
        title="Время архивации",
    )
    archiver_id: PydanticObjectId | None = Field(
        default=None,
        title="Идентификатор архиватора",
    )
    archiver_type: ArchiverType = Field(
        title="Тип архиватора",
    )

    class Settings:
        """
        Класс настроек заархивированной заявки
        """

        name = "ArchivedRequest"
