from datetime import datetime

from beanie import Document, PydanticObjectId
from file_manager import File
from pydantic import Field

from models.appeal.constants import AppealSource, AppealStatus, AppealType
from models.appeal.embs.appealer import Appealer
from models.appeal.embs.employee import DispatcherAS, EmployeeAS, ProviderAS
from models.appeal.embs.observers import ObserversAS
from models.appeal.embs.relations import RelationsAS
from models.base.binds import DepartmentBinds
from models.extra.attachment import ExpandedAttachment


class Appeal(Document):
    id: PydanticObjectId = Field(
        default_factory=PydanticObjectId,
        alias="_id",
        description="MongoDB document ObjectID",
    )
    subject: str = Field(
        title="Тема обращения",
    )
    description: str = Field(
        title="Описание обращения",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        title="Время создания обращения",
    )
    dispatcher: DispatcherAS | None = Field(
        default=None,
        title="Диспетчер принявший обращение",
    )
    appealer: Appealer = Field(
        title="Обращатор",
    )
    executor: EmployeeAS | None = Field(
        title="Исполнитель обращения",
    )
    relations: RelationsAS = Field(
        default_factory=RelationsAS,
        title="Связи обращения",
    )
    status: AppealStatus = Field(
        title="Статус обращения",
    )
    type: AppealType = Field(
        alias="_type",
        title="Тип обращения",
    )
    appealer_files: list[File] = Field(
        default_factory=list,
        title="Вложение обращения",
    )
    observers: ObserversAS = Field(
        default_factory=ObserversAS,
        title="Наблюдатели обращения",
    )
    answer: ExpandedAttachment | None = Field(
        default=None,
        title="Ответ на обращение",
    )
    add_answers: list[ExpandedAttachment] = Field(
        default_factory=list,
        title="Дополнительные ответы на обращение",
    )
    category_ids: set[PydanticObjectId] = Field(
        default_factory=set,
        title="Идентификаторы категорий обращения",
    )
    binds: DepartmentBinds = Field(
        alias="_binds",
        title="Привязки к организации и группе домов",
    )
    number: str = Field(
        title="Номер обращения",
    )
    provider: ProviderAS = Field(
        title="Организация принявшая обращение",
    )
    source: AppealSource = Field(
        title="Источник обращения",
    )
    incoming_number: str | None = Field(
        title="Входящий номер",
    )
    incoming_at: datetime | None = Field(
        title="Входящая дата",
    )
    deadline_at: datetime = Field(
        title="Крайний срок выполнения обращения",
    )
    for_beanie_err: None = Field(
        default=None,
        exclude=True,
    )  # При наличии keep_nulls = False в Settings класса, если при сохранении нету полей которые = None, beanie выдает ошибку pymongo.errors.OperationFailure  # При наличии keep_nulls = False в Settings класса, если при сохранении нету полей которые = None, beanie выдает ошибку pymongo.errors.OperationFailure
