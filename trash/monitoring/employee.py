"""
Модуль с дополнительными классами для заявки связанные с сотрудниками
"""

from enum import Enum

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from models.extra.external_control import ExternalControl
from models.extra.phone_number import PhoneNumber


class PositionRS(BaseModel):
    """
    Модель должности сотрудника
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор должности",
    )
    name: str = Field(
        title="Название должности",
    )


class DepartmentRS(BaseModel):
    """
    Модель отдела сотрудника
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор отдела",
    )
    name: str = Field(
        title="Название отдела",
    )


class ProviderRS(BaseModel):
    """
    Модель организации сотрудника
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор организации",
    )
    name: str = Field(
        title="Название организации",
    )


class EmployeeRS(BaseModel):
    """
    Класс стандартного сотрудника из заявки. RS = Request Scheme
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор связанной заявки",
    )
    short_name: str = Field(
        title="Фамилия И.О. сотрудника",
    )
    full_name: str = Field(
        title="Фамилия Имя Отчество сотрудника",
    )
    phone_numbers: list[PhoneNumber] = Field(
        default_factory=list,
        title="Номера телефонов сотрудника",
    )
    email: str | None = Field(
        default=None,
        title="Email сотрудника",
    )
    position: PositionRS = Field(
        title="Должность сотрудника",
    )
    department: DepartmentRS = Field(
        title="Отдел сотрудника",
    )
    provider: ProviderRS = Field(
        title="Организация сотрудника",
    )


class DispatcherRS(EmployeeRS):
    """
    Класс диспетчера из заявки.
    Такой же обычный сотрудник за исключением поля external_control для отслеживания того кто на самом деле принял заявку
    """

    external_control: ExternalControl | None = Field(
        default=None,
        title="Внешнее управление",
    )


class PersonInChargeType(str, Enum):
    """
    Типы ответственных сотрудников.
    Нужны для того чтобы различать одного и того же человека в разных статусах, например:
    диспетчер также является исполнителем, но если я попытаюсь удалить ответственное лицо по id
    удалятся все, диспетчер в роли диспетчера и диспетчер в роли исполнителя, хотя первый должен остаться
    """

    EXECUTOR = "executor"
    DISPATCHER = "dispatcher"
    SUPERVISOR = "supervisor"


class PersonInChargeRS(EmployeeRS):
    """
    Класс ответственного сотрудника за исполнение заявки
    """

    type: PersonInChargeType = Field(
        alias="_type",
        title="Тип ответственного человека",
    )
