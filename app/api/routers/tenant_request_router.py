"""
Модуль с роутером для работы с заявками для жителей
"""

from api.dependencies.auth import TenantDep
from api.qp_translators.request_qp_translator import TenantRequestQPTranslator
from beanie import PydanticObjectId
from fastapi import APIRouter, Query, Request, UploadFile, status
from file_manager import File
from schemes.request.tenant_request import (
    RequestTCatalogCScheme,
    RequestTCScheme,
    RequestTLScheme,
    RequestTRScheme,
)
from services.request.tenant_request_service import TenantRequestService

tenant_request_router = APIRouter(
    tags=["tenant_requests"],
)


@tenant_request_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=RequestTRScheme,
)
async def create_request(
    tenant: TenantDep,
    scheme: RequestTCScheme,
):
    """
    Создание заявки в свободной форме жителем
    """

    service = TenantRequestService(tenant)
    request = await service.create_request(scheme)
    return request


@tenant_request_router.post(
    path="/catalog/",
    status_code=status.HTTP_201_CREATED,
    response_model=RequestTRScheme,
)
async def create_catalog_request(
    tenant: TenantDep,
    scheme: RequestTCatalogCScheme,
):
    """
    Создание заявки в из каталога жителем
    """

    service = TenantRequestService(tenant)
    request = await service.create_catalog_request(scheme)
    return request


@tenant_request_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=list[RequestTLScheme],
)
async def get_request_list(
    tenant: TenantDep,
    req: Request,
):
    """
    Получение заявок жителем
    """

    params = await TenantRequestQPTranslator.parse(req.query_params)
    service = TenantRequestService(tenant)
    return await service.get_request_list(
        query_list=params.query_list,
        offset=params.offset,
        limit=params.limit,
        sort=params.sort,
    )


@tenant_request_router.get(
    path="/{request_id}/",
    status_code=status.HTTP_200_OK,
    response_model=RequestTRScheme,
)
async def get_request(
    tenant: TenantDep,
    request_id: PydanticObjectId,
):
    """
    Получение заявки по идентификатору жителем
    """

    service = TenantRequestService(tenant)
    return await service.get_request(request_id)


@tenant_request_router.patch(
    path="/{request_id}/rate/",
    status_code=status.HTTP_200_OK,
    response_model=RequestTRScheme,
)
async def rate_request(
    tenant: TenantDep,
    request_id: PydanticObjectId,
    score: int = Query(ge=0, le=5, title="Оценка обращения"),
):
    """
    Оценивание выполнения заявки жителем
    """

    service = TenantRequestService(tenant)
    return await service.rate_request(
        request_id=request_id,
        score=score,
    )


@tenant_request_router.post(
    path="/{request_id}/requester_attachment_files/",
    status_code=status.HTTP_200_OK,
    response_model=list[File],
)
async def upload_requester_attachment_files(
    tenant: TenantDep,
    request_id: PydanticObjectId,
    files: list[UploadFile],
):
    """
    Загрузка файлов вложения жителем
    """

    service = TenantRequestService(tenant)
    return await service.upload_requester_attachment_files(
        request_id=request_id,
        files=files,
    )
