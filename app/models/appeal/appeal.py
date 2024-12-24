from datetime import datetime

from beanie import PydanticObjectId
from file_manager import File
from pydantic import Field

from models.appeal.constants import AppealSource, AppealStatus, AppealType
from models.appeal.embs.answer import AnswerAS
from models.appeal.embs.appealer import Appealer
from models.appeal.embs.employee import DispatcherAS, EmployeeAS, ProviderAS
from models.appeal.embs.observers import ObserversAS
from models.appeal.embs.relations import RelationsAS
from models.base.binds import DepartmentBinds
from models.base_document import BaseDocument


class Appeal(BaseDocument):
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
        default=None,
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
    answer: AnswerAS | None = Field(
        default=None,
        title="Ответ на обращение",
    )
    is_answer_required: bool = Field(
        default=True,
        title="Нужен ли ответ на обращение",
    )
    revoked_at: datetime | None = Field(
        default=None,
        title="Время отзыва обращения",
    )
    rate: int = Field(
        default=0,
        ge=0,
        le=5,
        title="Оценка жителя",
    )
    add_answers: list[AnswerAS] = Field(
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
        default=None,
        title="Входящий номер",
    )
    incoming_at: datetime | None = Field(
        default=None,
        title="Входящая дата",
    )
    deadline_at: datetime = Field(
        title="Крайний срок выполнения обращения",
    )
