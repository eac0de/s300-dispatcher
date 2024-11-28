"""
Модуль для работы заявки через шлюз
"""

import asyncio

from beanie import PydanticObjectId
from fastapi import HTTPException
from starlette import status

from client.s300.api import S300API
from models.request.constants import RequestPayStatus
from models.request.request import RequestModel


class GatewayRequestService:
    """
    Сервис для работы с заявками через шлюх
    """

    @classmethod
    async def get_request_for_pay(cls, number: str) -> RequestModel:
        """
        Получение данных заявки для е оплаты

        Args:
            number (str): Номер заявки

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            RequestModel: Модель заявки
        """
        request = await cls._get_request_by_number(number)
        if request.commerce.pay_status != RequestPayStatus.WAIT or not request.commerce.catalog_items:
            raise HTTPException(
                detail="Request does not require payment",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return request

    @classmethod
    async def mark_request_as_paid(
        cls,
        request_id: PydanticObjectId,
    ):
        """
        Пометить заявку как оплаченную

        Args:
            request_id (PydanticObjectId): Идентификатор заявки
        """
        request = await cls._get_request(request_id)
        request.commerce.pay_status = RequestPayStatus.PAID
        asyncio.create_task(
            S300API.create_receipt_for_paid_request(
                request_id=request.id,
                provider_id=request.provider.id,
                tenant_email=request.requester.email,
                catalog_items=request.commerce.catalog_items,
            )
        )
        await request.save()

    @classmethod
    async def _get_request(
        cls,
        request_id: PydanticObjectId,
    ) -> RequestModel:
        request = await RequestModel.get(request_id)
        if not request:
            raise HTTPException(
                detail="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return request

    @classmethod
    async def _get_request_by_number(
        cls,
        number: str,
    ) -> RequestModel:
        request = await RequestModel.find_one({"number": number})
        if not request:
            raise HTTPException(
                detail="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return request
