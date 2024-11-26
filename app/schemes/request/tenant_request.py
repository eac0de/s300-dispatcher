"""
Модуль со схемами для создания, обновления и отображения заявки жителем
"""

from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from models.base.binds import ProviderHouseGroupBinds
from models.extra.attachment import Attachment
from models.request.constants import RequestType
from models.request.embs.employee import DispatcherRS
from models.request.embs.monitoring import MonitoringRS
from models.request.embs.rate import RateRS
from models.request.embs.relations import RelationsRS
from models.request.embs.resources import ResourcesRS
from models.request.request import RequestModel


class ExecutionRequestTCScheme(BaseModel):
    """
    Класс схемы модуля выполнения для создания заявки жителем
    """

    desired_start_at: datetime | None = Field(
        default=None,
        title="Желаемое время начала выполнения заявки",
    )
    desired_end_at: datetime | None = Field(
        default=None,
        title="Желаемое время окончания выполнения заявки",
    )


class RequestTCScheme(BaseModel):
    """
    Класс схемы заявки для ее создания жителем
    """

    type: RequestType = Field(
        alias="_type",
        title="Тип заявки",
    )
    description: str = Field(
        title="Описание заявки",
    )
    execution: ExecutionRequestTCScheme = Field(
        title="Выполнение заявки",
    )


class CatalogItemCommerceRequestTCatalogCScheme(BaseModel):
    """
    Класс схемы позиции каталога для создания заявки из каталога жителем
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор",
    )
    quantity: float = Field(
        title="Количество позиции",
    )


class CommerceRequestTCatalogCScheme(BaseModel):
    """
    Класс схемы модели коммерции для создания заявки из каталога жителем
    """

    catalog_items: list[CatalogItemCommerceRequestTCatalogCScheme] = Field(
        default_factory=list,
        title="Добавленные позиции",
    )


class RequestTCatalogCScheme(BaseModel):
    """
    Класс схемы заявки для ее создания жителем из каталога
    """

    commerce: CommerceRequestTCatalogCScheme = Field(
        title="Коммерческие данные заявки",
    )
    description: str | None = Field(
        title="Описание заявки",
    )


class RateExecutionRequestTRateUScheme(BaseModel):
    """
    Класс схемы оценки выполнения для ее обновления в заявке жителем
    """

    rate: int = Field(
        ge=1,
        le=5,
        title="Оценка заявки данным жителем",
    )


class ExecutionRequestTRateUScheme(BaseModel):
    """
    Класс схемы модели выполнения для обновления оценки выполнения заявки жителем
    """

    rates: list[RateExecutionRequestTRateUScheme] = Field(
        default_factory=list,
        title="Список оценок выполнения заявки",
    )


class RequestTRateUScheme(BaseModel):
    """
    Класс схемы заявки для обновления ее оценки выполнения жителем
    """

    execution: ExecutionRequestTRateUScheme = Field(
        title="Для выставления оценки",
    )


class ExecutionRequestTRLScheme(BaseModel):
    """
    Класс схемы модели выполнения для отображения заявки жителю
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
        title="Список оценок выполнения заявки",
    )
    total_rate: float = Field(
        ge=0,
        le=5,
        default=0,
        title="Средняя оценка выполнения заявки среди жителей",
    )
    delayed_until: datetime | None = Field(
        default=None,
        title="Время до которого перенесено выполнение заявки",
    )


class RequestTRScheme(RequestModel):
    """
    Класс схемы заявки для ее отображения жителю
    """

    binds: ProviderHouseGroupBinds = Field(
        alias="_binds",
        title="Привязки к организации и группе домов",
        exclude=True,
    )
    template_id: PydanticObjectId | None = Field(
        default=None,
        title="Ссылка на шаблон тела заявки",
        exclude=True,
    )
    administrative_supervision: bool = Field(
        default=False,
        title="Осуществляется ли административный надзор за заявкой",
        exclude=True,
    )
    housing_supervision: bool = Field(
        default=False,
        title="Осуществляется ли жилищный надзор (служба 004) за заявкой",
        exclude=True,
    )
    requester_attachments: list[Attachment] = Field(
        default_factory=list,
        title="Вложения заявителя",
    )
    related_call_id: PydanticObjectId | None = Field(
        title="Ссылка на связанный с заявкой звонок",
        exclude=True,
    )
    relations: RelationsRS | None = Field(
        default=None,
        title="Связанные заявки",
        exclude=True,
    )
    ticket_id: PydanticObjectId | None = Field(
        default=None,
        title="Идентификатор обращения",
        exclude=True,
    )
    dispatcher: DispatcherRS | None = Field(
        default=None,
        title="Диспетчер",
        exclude=True,
    )
    execution: ExecutionRequestTRLScheme = Field(
        title="Выполнение заявки",
    )
    resources: ResourcesRS = Field(
        default_factory=ResourcesRS,
        title="Ресурсы заявки",
        exclude=True,
    )
    monitoring: MonitoringRS = Field(
        default_factory=MonitoringRS,
        title="Информация по надзору за заявкой",
        exclude=True,
    )


class RequestTLScheme(RequestModel):
    """
    Класс схемы заявки для отображения заявок жителю списком
    """

    binds: ProviderHouseGroupBinds = Field(
        alias="_binds",
        title="Привязки к организации и группе домов",
        exclude=True,
    )
    administrative_supervision: bool = Field(
        default=False,
        title="Осуществляется ли административный надзор за заявкой",
        exclude=True,
    )
    housing_supervision: bool = Field(
        default=False,
        title="Осуществляется ли жилищный надзор (служба 004) за заявкой",
        exclude=True,
    )
    requester_attachments: list[Attachment] = Field(
        default_factory=list,
        title="Вложения заявителя",
    )
    relations: RelationsRS | None = Field(
        default=None,
        title="Связанные заявки",
        exclude=True,
    )
    dispatcher: DispatcherRS | None = Field(
        default=None,
        title="Диспетчер",
        exclude=True,
    )
    execution: ExecutionRequestTRLScheme = Field(
        title="Выполнение заявки",
    )
    resources: ResourcesRS = Field(
        default_factory=ResourcesRS,
        title="Ресурсы заявки",
        exclude=True,
    )
    monitoring: MonitoringRS = Field(
        default_factory=MonitoringRS,
        title="Информация по надзору за заявкой",
        exclude=True,
    )
