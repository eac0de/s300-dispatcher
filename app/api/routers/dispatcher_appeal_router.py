from beanie import PydanticObjectId
from fastapi import APIRouter, Request, status

from api.dependencies.auth import EmployeeDep
from api.qp_translators.appeal_qp_translator import DispatcherAppealsQPTranslator
from api.qp_translators.request_qp_translator import DispatcherRequestQPTranslator
from models.appeal.appeal import Appeal
from schemes.appeal.dispatcher_appeal import (
    AppealDCScheme,
    AppealDLScheme,
    AppealDRScheme,
)
from services.appeal.dispatcher_appeal_service import DispatcherAppealService

dispatcher_appeal_router = APIRouter(
    tags=["dispatcher_appeals"],
)


@dispatcher_appeal_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model_exclude={"binds"},
    response_model=Appeal,
)
async def create_appeal(
    employee: EmployeeDep,
    scheme: AppealDCScheme,
):
    """
    Создание обращения сотрудником
    """

    service = DispatcherAppealService(employee)
    appeal = await service.create_appeal(scheme)
    return appeal


@dispatcher_appeal_router.get(
    path="/",
    description="Получения списка обращений сотрудником.<br>" + DispatcherAppealsQPTranslator.get_docs(),
    status_code=status.HTTP_200_OK,
    response_model=list[AppealDLScheme],
)
async def get_request_list(
    employee: EmployeeDep,
    req: Request,
):
    """
    Получения списка обращений сотрудником.
    Для фильтрации есть определенные фильтры см. в модуле api/filters/appeal_qp_translator
    """

    params = await DispatcherRequestQPTranslator.parse(req.query_params)
    service = DispatcherAppealService(employee)
    requests = await service.get_appeals(
        query_list=params.query_list,
        offset=params.offset,
        limit=params.limit if params.limit and params.limit < 20 else 20,
        sort=params.sort,
    )
    return await requests.to_list()


@dispatcher_appeal_router.get(
    path="/{appeal_id}/",
    status_code=status.HTTP_200_OK,
    response_model=AppealDRScheme,
)
async def get_request(
    employee: EmployeeDep,
    appeal_id: PydanticObjectId,
):
    """
    Получение обращения по идентификатору сотрудником
    """

    service = DispatcherAppealService(employee)
    return await service.get_appeal(appeal_id)
