"""
Модуль с дополнительным классом для заявки - вложения
"""

from datetime import datetime

from beanie import PydanticObjectId
from file_manager import File
from pydantic import BaseModel, Field

from models.appeal.embs.employee import PositionAS


class Attachment(BaseModel):
    """
    Класс вложения
    """

    files: list[File] = Field(
        default_factory=list,
        title="Файлы вложения",
    )
    comment: str = Field(
        default="",
        title="Комментарий",
    )


class EmployeeExpandedAttachment(BaseModel):
    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор связанной заявки",
    )
    short_name: str = Field(
        title="Фамилия И.О. сотрудника",
    )
    position: PositionAS = Field(
        title="Должность сотрудника",
    )


class ExpandedAttachment(Attachment):
    id: PydanticObjectId = Field(
        default_factory=PydanticObjectId,
        alias="_id",
        description="Идентификатор вложения",
    )
    employee: EmployeeExpandedAttachment = Field(
        title="Сотрудник",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        title="Время создания вложения",
    )
