"""
Модуль для работы заявки через шлюз
"""

from beanie import PydanticObjectId
from fastapi import HTTPException
from starlette import status

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
        if request.commerce.pay_status != RequestPayStatus.PAID or not request.commerce.catalog_items:
            raise HTTPException(
                detail="Request does not require payment",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return request

    @classmethod
    async def update_pay_status(
        cls,
        request_id: PydanticObjectId,
        pay_status: RequestPayStatus,
    ):
        """
        Обновление статусы оплаты заявки

        Args:
            request_id (PydanticObjectId): Идентификатор заявки
            pay_status (RequestPayStatus): Статус оплаты
        """
        request = await cls._get_request(request_id)
        request.commerce.pay_status = pay_status
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
