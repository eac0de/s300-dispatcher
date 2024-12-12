"""
Модуль с дополнительными классами для заявки связанные с сотрудниками
"""

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from models.extra.external_control import ExternalControl
from models.extra.phone_number import PhoneNumber


class PositionAS(BaseModel):
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


class DepartmentAS(BaseModel):
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


class ProviderAS(BaseModel):
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


class EmployeeAS(BaseModel):
    """
    Класс стандартного сотрудника из обращения. AS = Appeal Scheme
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
    position: PositionAS = Field(
        title="Должность сотрудника",
    )
    department: DepartmentAS = Field(
        title="Отдел сотрудника",
    )


class DispatcherAS(EmployeeAS):
    """
    Класс диспетчера из обращения.
    Такой же обычный сотрудник за исключением поля external_control для отслеживания того кто на самом деле принял заявку
    """

    external_control: ExternalControl | None = Field(
        default=None,
        title="Внешнее управление",
    )
