"""
Модуль с роутером для работы с заявками для жителей
"""

from api.dependencies.auth import TenantDep
from api.qp_translators.appeal_qp_translator import TenantAppealsQPTranslator
from beanie import PydanticObjectId
from fastapi import APIRouter, Query, Request, UploadFile, status
from file_manager import File
from schemes.appeal.tenant_appeal import AppealTRLScheme
from services.appeal.tenant_appeal_service import TenantAppealService

tenant_appeal_router = APIRouter(
    tags=["tenant_appeals"],
)


@tenant_appeal_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=list[AppealTRLScheme],
)
async def get_appeal_list(
    tenant: TenantDep,
    req: Request,
):
    """
    Получение заявок жителем
    """

    params = await TenantAppealsQPTranslator.parse(req.query_params)
    service = TenantAppealService(tenant)
    appeals = await service.get_appeal_list(
        query_list=params.query_list,
        offset=params.offset,
        limit=params.limit,
        sort=params.sort,
    )
    return await appeals.to_list()


@tenant_appeal_router.get(
    path="/{appeal_id}/",
    status_code=status.HTTP_200_OK,
    response_model=AppealTRLScheme,
)
async def get_appeal(
    tenant: TenantDep,
    appeal_id: PydanticObjectId,
):
    """
    Получение заявки по идентификатору жителем
    """

    service = TenantAppealService(tenant)
    return await service.get_appeal(appeal_id)


@tenant_appeal_router.patch(
    path="/{appeal_id}/rate/",
    status_code=status.HTTP_200_OK,
    response_model=AppealTRLScheme,
)
async def rate_appeal(
    tenant: TenantDep,
    appeal_id: PydanticObjectId,
    score: int = Query(ge=0, le=5, title="Оценка обращения"),
):
    service = TenantAppealService(tenant)
    return await service.rate_appeal(
        appeal_id=appeal_id,
        score=score,
    )


@tenant_appeal_router.post(
    path="/{appeal_id}/appealer_files/",
    status_code=status.HTTP_200_OK,
    response_model=list[File],
)
async def upload_appealer_files(
    tenant: TenantDep,
    appeal_id: PydanticObjectId,
    files: list[UploadFile],
):
    """
    Загрузка файлов вложения жителем
    """

    service = TenantAppealService(tenant)
    return await service.upload_appealer_files(
        appeal_id=appeal_id,
        files=files,
    )
