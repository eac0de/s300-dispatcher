"""
Модуль с классом заявки
"""

from datetime import datetime

from pydantic import Field

from models.base.binds import ProviderHouseGroupBinds
from models.base_document import BaseDocument
from models.extra.attachment import Attachment
from models.request.categories_tree import (
    RequestCategory,
    RequestSubcategory,
    RequestWorkArea,
)
from models.request.constants import (
    RequestSource,
    RequestStatus,
    RequestTag,
    RequestType,
)
from models.request.embs.action import (
    ActionRS,
    LiftShutdownActionRS,
    StandpipeShutdownActionRS,
)
from models.request.embs.area import AreaRS
from models.request.embs.commerce import CommerceRS
from models.request.embs.employee import DispatcherRS, ProviderRS
from models.request.embs.execution import ExecutionRS
from models.request.embs.house import HouseRS
from models.request.embs.relations import RelationsRS
from models.request.embs.requester import (
    EmployeeRequester,
    OtherEmployeeRequester,
    OtherPersonRequester,
    TenantRequester,
)
from models.request.embs.resources import ResourcesRS


class RequestModel(BaseDocument):
    """
    Класс заявки
    """

    binds: ProviderHouseGroupBinds = Field(
        alias="_binds",
        title="Привязки к организации и группе домов",
    )
    type: RequestType = Field(
        alias="_type",
        title="Тип заявки",
    )
    area: AreaRS | None = Field(
        default=None,
        title="Квартира по заявке",
    )
    house: HouseRS = Field(
        title="Дом по заявке",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        title="Дата создания заявки",
    )
    number: str = Field(
        title="Уникальный номер заявки",
    )
    requester: TenantRequester | OtherPersonRequester | EmployeeRequester | OtherEmployeeRequester = Field(
        title="Заявитель",
    )
    description: str = Field(
        title="Описание заявки",
    )
    category: RequestCategory = Field(
        title="Категория заявки",
    )
    subcategory: RequestSubcategory | None = Field(
        default=None,
        title="Подкатегория заявки",
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
        default=False,
        title="Осуществляется ли административный надзор за заявкой",
    )
    housing_supervision: bool = Field(
        default=False,
        title="Осуществляется ли жилищный надзор (служба 004) за заявкой",
    )
    tag: RequestTag = Field(
        default=RequestTag.CURRENT,
        title="Тег заявки",
    )
    requester_attachment: Attachment = Field(
        default_factory=Attachment,
        title="Вложение заявителя",
    )
    status: RequestStatus = Field(
        default=RequestStatus.ACCEPTED,
        title="Статус заявки",
    )
    status_updated_at: datetime = Field(
        default_factory=datetime.now,
        title="Время смены заявки",
    )
    relations: RelationsRS = Field(
        default_factory=RelationsRS,
        title="Связи с заявкой",
    )
    source: RequestSource = Field(
        title="Источник заявки",
    )
    dispatcher: DispatcherRS | None = Field(
        default=None,
        title="Диспетчер",
    )
    provider: ProviderRS = Field(
        title="Организация, владелец заявки",
    )
    is_public: bool = Field(
        default=False,
        title="Публичная ли заявка",
        description="Если публичная ее могут видеть все жители дома",
    )
    execution: ExecutionRS = Field(
        title="Выполнение заявки",
    )
    commerce: CommerceRS = Field(
        default_factory=CommerceRS,
        title="Коммерческие данные заявки",
    )
    resources: ResourcesRS = Field(
        default_factory=ResourcesRS,
        title="Ресурсы заявки",
    )

    class Settings:
        """
        Класс настройки заявки
        """

        name = "Request"
