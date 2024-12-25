"""
Модуль с дополнительным классом заявки связанным с контролем над исполнением
"""

from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from models.request.embs.employee import PersonInChargeRS


class ControlMessageSender(BaseModel):
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


class ControlMessageRS(BaseModel):
    """
    Класс сообщения от контролирующего исполнение заявки
    """

    message: str = Field(
        title="Сообщение",
    )
    employee: ControlMessageSender = Field(
        title="Создатель сообщения",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        title="Время создания сообщения",
    )


class MonitoringRS(BaseModel):
    """
    Класс заявки связанным с ее мониторингом
    """

    control_messages: list[ControlMessageRS] = Field(
        default_factory=list,
        title="Сообщения от контролирующих лиц",
    )
    persons_in_charge: list[PersonInChargeRS] = Field(
        default_factory=list,
        title="Ответственные за заявку лица",
    )
