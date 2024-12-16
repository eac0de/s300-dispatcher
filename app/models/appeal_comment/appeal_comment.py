from datetime import datetime

from beanie import Document, PydanticObjectId
from file_manager import File
from pydantic import BaseModel, Field


class EmployeeAppealComment(BaseModel):
    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор связанной заявки",
    )
    short_name: str = Field(
        title="Фамилия И.О. сотрудника",
    )
    position_name: str = Field(
        title="Название должности сотрудника",
    )


class AppealComment(Document):
    id: PydanticObjectId = Field(
        default_factory=PydanticObjectId,
        alias="_id",
        description="MongoDB document ObjectID",
    )
    appeal_id: PydanticObjectId = Field(
        title="Идентификатор обращения",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        title="Время создания комментария",
    )
    message: str = Field(
        title="Текст комментария",
    )
    files: list[File] = Field(
        default_factory=list,
        title="Файлы комментария",
    )
    employee: EmployeeAppealComment = Field(
        title="Автор комментария",
    )
    read_by: set[PydanticObjectId] = Field(
        default_factory=set,
        title="Список идентификаторов пользователей прочитавших комментарий",
    )
