"""
Модуль с дополнительным классом заявки связанным с исполнением заявки
"""

from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from models.extra.attachment import Attachment
from models.request.embs.employee import EmployeeRS, ProviderRS


class RateRS(BaseModel):
    """
    Класс оценки выполненных по заявке работ
    """

    tenant_id: PydanticObjectId = Field(
        title="Идентификатор человека проставившего оценку",
    )
    score: int = Field(
        ge=1,
        le=5,
        title="Оценка выполнения заявки (от 1 до 5)",
    )
    rated_at: datetime = Field(
        default_factory=datetime.now,
        title="Дата и время выставления оценки",
    )


class ExecutionRS(BaseModel):
    """
    Класс заявки связанным с ее исполнением
    """

    desired_start_at: datetime | None = Field(
        default=None,
        title="Желаемое время начала выполнения заявки",
    )
    desired_end_at: datetime | None = Field(
        default=None,
        title="Желаемое время окончания выполнения заявки",
    )
    start_at: datetime | None = Field(
        default=None,
        title="Фактическое время начала выполнения заявки",
    )
    end_at: datetime | None = Field(
        default=None,
        title="Фактическое время окончания выполнения заявки",
    )
    provider: ProviderRS = Field(
        title="Организация исполняющая заявку",
    )
    employees: list[EmployeeRS] = Field(
        default_factory=list,
        title="Сотрудники исполняющие заявку",
    )
    act: Attachment = Field(
        default_factory=Attachment,
        title="Акт выполненных работ",
    )
    attachment: Attachment = Field(
        default_factory=Attachment,
        title="Вложение о выполненных работ",
    )
    description: str | None = Field(
        default=None,
        title="Описание выполненных работ",
    )
    is_partially: bool = Field(
        default=False,
        title="Выполнена частично",
    )
    warranty_until: datetime | None = Field(
        default=None,
        title="Гарантия по",
    )
    rates: list[RateRS] = Field(
        default_factory=list,
        title="Список оценок выполнения работы по заявке",
    )
    average_rating: float = Field(
        ge=0,
        le=5,
        default=0,
        title="Средняя оценка выполнения заявки среди жителей",
    )
    delayed_until: datetime | None = Field(
        default=None,
        title="Время до которого перенесено выполнение заявки",
    )
