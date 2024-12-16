"""
Модуль с дополнительным классом - связей заявки с другими классами или другими заявками
"""

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from models.request.constants import RequestStatus


class RequestRelationsRS(BaseModel):
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
    status: RequestStatus = Field(
        title="Статус связанной заявки",
    )


class AppealRelationsRS(BaseModel):
    """
    Класс связанного обращения
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор связанного обращения",
    )
    number: str = Field(
        title="Номер связанного обращения",
    )


class RelationsRS(BaseModel):
    """
    Класс связей заявки с другими классами или другими заявками
    """

    requests: list[RequestRelationsRS] = Field(
        default_factory=list,
        title="Список связанных заявок",
    )
    call_id: PydanticObjectId | None = Field(
        default=None,
        title="Ссылка на связанный с заявкой звонок",
    )
    appeal: AppealRelationsRS | None = Field(
        default=None,
        title="Ссылка на обращение, которое создано из этой заявки",
    )
    template_id: PydanticObjectId | None = Field(
        default=None,
        title="Ссылка на шаблон тела заявки",
    )
