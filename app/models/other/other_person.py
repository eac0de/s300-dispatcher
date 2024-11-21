"""
Модуль с моделью стороннего лица 
"""

from beanie import Document, PydanticObjectId
from pydantic import EmailStr, Field

from models.base.binds import ProviderBinds
from models.extra.phone_number import PhoneNumber


class OtherPerson(Document):
    """
    Модель стороннего лица
    """

    id: PydanticObjectId = Field(
        default_factory=PydanticObjectId,
        alias="_id",
        description="MongoDB document ObjectID",
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
    email: EmailStr | None = Field(
        default=None,
        title="Email стороннего лица",
    )
    binds: ProviderBinds = Field(
        alias="_binds",
        title="Привязки к организации и группе домов",
    )
