"""
Модуль со схемами для обновления статуса и ресурсов заявки работником
"""

from pydantic import BaseModel, Field

from models.request.constants import RequestPayStatus


class RequestGPayStatusUScheme(BaseModel):
    """
    Схема для обновления статуса оплаты заявки через шлюз
    """

    pay_status: RequestPayStatus = Field(
        title="Статус оплаты заявки",
    )
