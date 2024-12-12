"""
Модуль с дополнительным классами заявителя
"""

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from models.extra.phone_number import PhoneNumber
from models.request.embs.area import AreaRS
from models.request.embs.house import HouseRS


class Appealer(BaseModel):
    """
    Класс обращатора
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор обращатора",
    )
    short_name: str = Field(
        title="Фамилия И.О. обращатора",
    )
    full_name: str = Field(
        title="Фамилия Имя Отчество обращатора",
    )
    phone_numbers: list[PhoneNumber] = Field(
        default_factory=list,
        title="Номера телефонов обращатора",
    )
    email: str | None = Field(
        default=None,
        title="Email обращатора",
    )
    area: AreaRS = Field(
        title="Квартира обращатора",
    )
    house: HouseRS = Field(
        title="Дом обращатора",
    )
