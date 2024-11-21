"""
Модуль с дополнительным классом для заявки - коммерция.
Отвечает за коммерческие данные заявки
"""

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from models.request.constants import RequestPayStatus


class CatalogItemCommerceRS(BaseModel):
    """
    Класс заказанной позиции из каталога
    """

    name: str = Field(
        title="Название позиции",
    )
    price: int = Field(
        ge=100,
        title="Цена за единицу позиции",
    )
    quantity: float = Field(
        gt=0,
        title="Количество позиции",
    )
    item_id: PydanticObjectId = Field(
        title="Идентификатор позиции в каталоге",
    )


class CommerceRS(BaseModel):
    """
    Класс коммерции
    """

    pay_status: RequestPayStatus = Field(
        default=RequestPayStatus.NO_CHARGE,
        title="Статус оплаты заявки",
    )
    receipt_id: PydanticObjectId | None = Field(
        default=None,
        title="Идентификатор чека об оплате",
    )
    catalog_items: list[CatalogItemCommerceRS] = Field(
        default_factory=list,
        title="Добавленные позиции",
    )
