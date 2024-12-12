from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from models.appeal.appeal import Appeal
from models.appeal.constants import AppealStatus, AppealType
from models.base.binds import DepartmentBinds
from schemes.extra.only_id import OnlyIdScheme


class ObserversDCScheme(BaseModel):
    employees: list[OnlyIdScheme] = Field(
        default_factory=list,
    )
    departments: list[OnlyIdScheme] = Field(
        default_factory=list,
    )


class AppealDCScheme(BaseModel):
    subject: str = Field(
        title="Тема обращения",
    )
    description: str = Field(
        title="Описание обращения",
    )
    appealer: OnlyIdScheme = Field(
        title="Обращатор",
    )
    status: AppealStatus = Field(
        title="Статус обращения",
    )
    type: AppealType = Field(
        title="Тип обращения",
    )
    observers: ObserversDCScheme = Field(
        title="Наблюдатели обращения",
    )
    category_ids: set[PydanticObjectId] = Field(
        title="Идентификаторы категорий обращения",
    )
    incoming_number: str | None = Field(
        title="Входящий номер",
    )
    incoming_at: datetime | None = Field(
        title="Входящая дата",
    )


class AppealDRScheme(Appeal):
    binds: DepartmentBinds = Field(
        alias="_binds",
        title="Привязки к организации и группе домов",
        exclude=True,
    )


class AppealDLScheme(Appeal):
    binds: DepartmentBinds = Field(
        alias="_binds",
        title="Привязки к организации и группе домов",
        exclude=True,
    )
