"""
Модуль с моделью стороннего сотрудника 
"""

from beanie import Document, PydanticObjectId
from pydantic import EmailStr, Field

from models.base.binds import ProviderBinds
from models.extra.phone_number import PhoneNumber


class OtherEmployee(Document):
    """
    Модель стороннего сотрудника
    """

    id: PydanticObjectId = Field(
        default_factory=PydanticObjectId,
        alias="_id",
        description="MongoDB document ObjectID",
    )
    short_name: str = Field(
        title="Фамилия И.О. стороннего сотрудника",
    )
    full_name: str = Field(
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
    position_name: str = Field(
        title="Должность стороннего сотрудника",
    )
    provider_id: PydanticObjectId = Field(
        title="Организации стороннего сотрудника",
    )
    binds: ProviderBinds = Field(
        alias="_binds",
        title="Привязки к организации и группе домов",
    )