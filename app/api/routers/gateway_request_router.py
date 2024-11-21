"""
Модуль с роутером для запросов из других микросервисов
"""

from beanie import PydanticObjectId
from fastapi import APIRouter, Query, status

from api.dependencies.auth import GatewayDep
from models.request.constants import RequestPayStatus
from models.request.request import RequestModel
from services.request.gateway_request_service import GatewayRequestService

gateway_request_router = APIRouter(
    tags=["gateway_requests"],
)


@gateway_request_router.get(
    path="/for_pay",
    status_code=status.HTTP_200_OK,
    response_model_include={"id", "number", "commerce"},
    response_model=RequestModel,
)
async def get_request_for_pay(
    _: GatewayDep,
    request_number: str = Query(),
):
    """
    Получение информации о заявке для ее оплаты
    """

    service = GatewayRequestService()
    return await service.get_request_for_pay(request_number)


@gateway_request_router.patch(
    path="/{request_id}/pay_status/{pay_status}",
    status_code=status.HTTP_200_OK,
)
async def update_pay_status(
    _: GatewayDep,
    request_id: PydanticObjectId,
    pay_status: RequestPayStatus,
):
    """
    Обновление статуса оплаты заявки
    """

    service = GatewayRequestService()
    await service.update_pay_status(
        request_id=request_id,
        pay_status=pay_status,
    )
