from datetime import datetime

from beanie import PydanticObjectId
from file_manager import File
from pydantic import BaseModel, Field

from models.appeal.embs.employee import PositionAS


class EmployeeAnswerAS(BaseModel):
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


class AnswerAS(BaseModel):
    id: PydanticObjectId = Field(
        default_factory=PydanticObjectId,
        alias="_id",
        description="Идентификатор вложения",
    )
    files: list[File] = Field(
        default_factory=list,
        title="Файлы вложения",
    )
    text: str = Field(
        title="Комментарий",
    )
    employee: EmployeeAnswerAS = Field(
        title="Сотрудник",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        title="Время создания вложения",
    )
