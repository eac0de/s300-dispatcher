"""
Модуль со схемами для создания, обновления и отображения сторонних лиц
"""

from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr, Field

from models.base.binds import ProviderBinds
from models.extra.phone_number import PhoneNumber
from models.other.other_employee import OtherEmployee
from models.other.other_person import OtherPerson
from models.other.other_provider import OtherProvider


class OtherEmployeeCScheme(BaseModel):
    """
    Класс схемы для создания стороннего сотрудника
    """

    full_name: str = Field(
        title="Фамилия Имя Отчество стороннего сотрудника",
    )
    phone_numbers: list[PhoneNumber] = Field(
        title="Номера телефонов стороннего сотрудника",
    )
    email: EmailStr | None = Field(
        title="Email стороннего сотрудника",
    )
    position_name: str = Field(
        title="Должность стороннего сотрудника",
    )
    provider_id: PydanticObjectId = Field(
        title="Идентификатор организации стороннего сотрудника",
    )


class OtherEmployeeUScheme(BaseModel):
    """
    Класс схемы для обновления стороннего сотрудника
    """

    full_name: str | None = Field(
        default=None,
        title="Фамилия Имя Отчество стороннего сотрудника",
    )
    phone_numbers: list[PhoneNumber] = Field(
        default_factory=list,
        title="Номера телефонов стороннего сотрудника",
    )
    email: EmailStr | None = Field(
        default=None,
        title="Email стороннего сотрудника",
    )
    position_name: str | None = Field(
        default=None,
        title="Должность стороннего сотрудника",
    )
    provider_id: PydanticObjectId | None = Field(
        default=None,
        title="Идентификатор организации стороннего сотрудника",
    )


class OtherPersonCScheme(BaseModel):
    """
    Класс схемы для создания или обновления стороннего лица
    """

    full_name: str = Field(
        title="Фамилия Имя Отчество жителя",
    )
    phone_numbers: list[PhoneNumber] = Field(
        title="Номера телефонов стороннего лица",
    )
    email: EmailStr | None = Field(
        title="Email стороннего лица",
    )


class OtherPersonUScheme(BaseModel):
    """
    Класс схемы для создания или обновления стороннего лица
    """

    full_name: str | None = Field(
        default=None,
        title="Фамилия Имя Отчество жителя",
    )
    phone_numbers: list[PhoneNumber] = Field(
        default_factory=list,
        title="Номера телефонов стороннего лица",
    )
    email: EmailStr | None = Field(
        default=None,
        title="Email стороннего лица",
    )


class OtherProviderCScheme(BaseModel):
    """
    Класс схемы для создания или обновления сторонней организации
    """

    name: str = Field(
        title="Название сторонней организации",
    )
    inn: str = Field(
        pattern=r"\d{10}",
        title="ИНН сторонней организации",
    )
    ogrn: str = Field(
        pattern=r"\d{13}",
        title="ОГРН сторонней организации",
    )


class OtherProviderUScheme(BaseModel):
    """
    Класс схемы для создания или обновления сторонней организации
    """

    name: str | None = Field(
        default=None,
        title="Название сторонней организации",
    )
    inn: str | None = Field(
        default=None,
        pattern=r"\d{10}",
        title="ИНН сторонней организации",
    )
    ogrn: str | None = Field(
        default=None,
        pattern=r"\d{13}",
        title="ОГРН сторонней организации",
    )


class OtherPersonRScheme(OtherPerson):
    """
    Класс схемы для отображения стороннего сотрудника
    """

    binds: ProviderBinds = Field(
        alias="_binds",
        title="Привязки к организации и группе домов",
        exclude=True,
    )


class OtherEmployeeRScheme(OtherEmployee):
    """
    Класс схемы для отображения стороннего лица
    """

    binds: ProviderBinds = Field(
        alias="_binds",
        title="Привязки к организации и группе домов",
        exclude=True,
    )


class OtherProviderRScheme(OtherProvider):
    """
    Класс схемы для отображения сторонней организации
    """

    binds: ProviderBinds = Field(
        alias="_binds",
        title="Привязки к организации и группе домов",
        exclude=True,
    )
