"""
Модуль с дополнительным классами заявителя
"""

from enum import Enum
from typing import Literal

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from models.cache.tenant import AreaTCS, HouseTCS
from models.extra.phone_number import PhoneNumber
from models.other.other_provider import OtherProvider
from models.request.embs.employee import ProviderRS


class RequesterType(str, Enum):
    """
    Типы заявителей
    """

    OTHER_EMPLOYEE = "other_employee"
    OTHER_PERSON = "other_person"
    EMPLOYEE = "employee"
    TENANT = "tenant"


class Requester(BaseModel):
    """
    Общий класс заявителя со всеми общими полями
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор жителя",
    )
    short_name: str = Field(
        title="Фамилия И.О. лица",
    )
    full_name: str = Field(
        title="Фамилия Имя Отчество жителя",
    )
    phone_numbers: list[PhoneNumber] = Field(
        default_factory=list,
        title="Номера телефонов стороннего лица",
    )
    email: str | None = Field(
        default=None,
        title="Email стороннего лица",
    )


class OtherPersonRequester(Requester):
    """
    Класс заявителя - стороннего лица
    """

    type: Literal[RequesterType.OTHER_PERSON] = Field(
        alias="_type",
        default=RequesterType.OTHER_PERSON,
        title="Тип заявителя - стороннего лица",
    )


class TenantRequester(Requester):
    """
    Класс заявителя - жителя
    """

    type: Literal[RequesterType.TENANT] = Field(
        alias="_type",
        default=RequesterType.TENANT,
        title="Тип заявителя - жителя",
    )
    area: AreaTCS = Field(
        title="Квартира жителя",
    )
    house: HouseTCS = Field(
        title="Дом жителя",
    )


class EmployeeRequester(Requester):
    """
    Класс заявителя - сотрудник
    """

    type: Literal[RequesterType.EMPLOYEE] = Field(
        alias="_type",
        default=RequesterType.EMPLOYEE,
        title="Тип заявителя - сотрудника",
    )
    position_name: str = Field(
        title="Название должности",
    )
    provider: ProviderRS = Field(
        title="Организация",
    )


class OtherEmployeeRequester(EmployeeRequester):
    """
    Класс заявителя - сторонний сотрудник
    """

    type: Literal[RequesterType.OTHER_EMPLOYEE] = Field(
        alias="_type",
        default=RequesterType.OTHER_EMPLOYEE,
        title="Тип заявителя - стороннего сотрудника",
    )
    provider: OtherProvider = Field(
        title="Организация стороннего сотрудника",
    )
