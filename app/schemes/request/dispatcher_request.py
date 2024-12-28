"""
Модуль со схемами для создания, обновления определенных полей и отображения заявки работником
"""

from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from models.base.binds import ProviderHouseGroupBinds
from models.extra.attachment import Attachment
from models.request.categories_tree import (
    RequestCategory,
    RequestSubcategory,
    RequestWorkArea,
)
from models.request.constants import RequestTag, RequestType
from models.request.embs.action import (
    ActionRS,
    LiftShutdownActionRS,
    StandpipeShutdownActionRS,
)
from models.request.embs.employee import EmployeeRS
from models.request.embs.requester import RequesterType
from models.request.request import RequestModel
from schemes.extra.only_id import OnlyIdScheme


class RequesterRequestDCScheme(BaseModel):
    """
    Класс схемы заявителя для создания заявки работником
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор жителя",
    )
    type: RequesterType = Field(
        alias="_type",
        title="Тип заявителя",
    )


class RelationsRequestDCUScheme(BaseModel):
    """
    Класс схемы связей
    """

    template_id: PydanticObjectId | None = Field(
        default=None,
        title="Ссылка на шаблон тела заявки",
    )
    requests: list[OnlyIdScheme] = Field(
        default_factory=list,
        title="Список связанных заявок",
    )


class ExecutionRequestDCScheme(BaseModel):
    """
    Класс схемы модели выполнения для создания заявки работником
    """

    desired_start_at: datetime | None = Field(
        default=None,
        title="Желаемое время начала выполнения заявки работником",
    )
    desired_end_at: datetime | None = Field(
        default=None,
        title="Желаемое время окончания выполнения заявки работником",
    )


class RequestDCScheme(BaseModel):
    """
    Класс схемы заявки для ее создания работником
    """

    type: RequestType = Field(
        alias="_type",
        title="Тип заявки работником",
    )
    area: OnlyIdScheme | None = Field(
        default=None,
        title="Квартира по заявке",
    )
    house: OnlyIdScheme = Field(
        title="Дом по заявке",
    )
    requester: RequesterRequestDCScheme = Field(
        title="Заявитель",
    )
    description: str = Field(
        title="Описание заявки работником",
    )
    category: RequestCategory = Field(
        title="Категория заявки работником",
    )
    subcategory: RequestSubcategory | None = Field(
        default=None,
        title="Подкатегория заявки работником",
    )
    work_area: RequestWorkArea | None = Field(
        default=None,
        title="Область работ по заявке",
    )
    actions: list[ActionRS | LiftShutdownActionRS | StandpipeShutdownActionRS] = Field(
        default_factory=list,
        title="Действия по заявке",
        description="Если необходимы какие-то отключения, например отключение электроснабжения или стояка",
    )
    administrative_supervision: bool = Field(
        title="Осуществляется ли административный надзор за заявкой",
    )
    housing_supervision: bool = Field(
        title="Осуществляется ли жилищный надзор (служба 004) за заявкой",
    )
    tag: RequestTag = Field(
        title="Тег заявки работником",
    )
    relations: RelationsRequestDCUScheme = Field(
        default_factory=RelationsRequestDCUScheme,
        title="Связанные заявки работником",
    )
    is_public: bool = Field(
        title="Публичная ли заявка",
        description="Если публичная ее могут видеть все жители дома",
    )
    execution: ExecutionRequestDCScheme = Field(
        title="Выполнение заявки работником",
    )


class ExecutionRequestDUScheme(BaseModel):
    """
    Класс схемы модели выполнения для обновления заявки работником
    """

    desired_start_at: datetime | None = Field(
        default=None,
        title="Желаемое время начала выполнения заявки работником",
    )
    desired_end_at: datetime | None = Field(
        default=None,
        title="Желаемое время окончания выполнения заявки работником",
    )
    act: Attachment | None = Field(
        default=None,
        title="Акт выполненных работ",
    )
    attachment: Attachment | None = Field(
        default=None,
        title="Вложение о выполненных работ",
    )


class RequestDUScheme(BaseModel):
    """
    Класс схемы заявки для ее обновления работником
    """

    description: str | None = Field(
        default=None,
        title="Описание заявки работником",
    )
    category: RequestCategory | None = Field(
        default=None,
        title="Категория заявки работником",
    )
    subcategory: RequestSubcategory | None = Field(
        default=None,
        title="Подкатегория заявки работником",
    )
    work_area: RequestWorkArea | None = Field(
        default=None,
        title="Область работ по заявке",
    )
    actions: list[ActionRS | LiftShutdownActionRS | StandpipeShutdownActionRS] | None = Field(
        default=None,
        title="Действия по заявке",
        description="Если необходимы какие-то отключения, например отключение электроснабжения или стояка",
    )
    administrative_supervision: bool | None = Field(
        default=None,
        title="Осуществляется ли административный надзор за заявкой",
    )
    housing_supervision: bool | None = Field(
        default=None,
        title="Осуществляется ли жилищный надзор (служба 004) за заявкой",
    )
    tag: RequestTag | None = Field(
        default=None,
        title="Тег заявки работником",
    )
    is_public: bool | None = Field(
        default=None,
        title="Публичная ли заявка",
        description="Если публичная ее могут видеть все жители дома",
    )
    relations: RelationsRequestDCUScheme | None = Field(
        default=None,
        title="Связи заявки",
    )
    execution: ExecutionRequestDUScheme | None = Field(
        default=None,
        title="Выполнение заявки",
    )
    requester_attachment: Attachment | None = Field(
        default=None,
        title="Вложение заявителя",
    )


class RequestDRScheme(RequestModel):
    """
    Класс схемы заявки для ее отображения работнику
    """

    dispatcher: EmployeeRS | None = Field(
        default=None,
        title="Диспетчер принявший заявку",
    )
    binds: ProviderHouseGroupBinds = Field(
        alias="_binds",
        title="Привязки к организации и группе домов",
        exclude=True,
    )


class RequestDLScheme(RequestModel):
    """
    Класс схемы для отображения списка заявок работнику
    """

    dispatcher: EmployeeRS | None = Field(
        default=None,
        title="Диспетчер принявший заявку",
    )
    binds: ProviderHouseGroupBinds = Field(
        alias="_binds",
        title="Привязки к организации и группе домов",
        exclude=True,
    )
