"""
Модуль с дополнительным классом заявки связанным с контролем над исполнением
"""

from datetime import datetime

from pydantic import BaseModel, Field

from models.request.embs.employee import PersonInChargeRS


class ControlMessageRS(BaseModel):
    """
    Класс сообщения от контролирующего исполнение заявки
    """

    message: str = Field(
        title="Сообщение",
    )
    controller_short_name: str = Field(
        title="Фамилия И.О. контролирующего лица",
    )
    controller_position_name: str = Field(
        title="Название должности контролирующего лица",
    )
    controller_provider_name: str = Field(
        title="Название организации контролирующего лица",
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
