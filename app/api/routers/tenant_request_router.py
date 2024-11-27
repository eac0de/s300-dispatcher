"""
Модуль с роутером для работы с заявками для жителей
"""

from beanie import PydanticObjectId
from fastapi import APIRouter, Request, UploadFile, status

from api.dependencies.auth import TenantDep
from api.filters.request_filter import TenantRequestFilter
from schemes.request.tenant_request import (
    RequestTCatalogCScheme,
    RequestTCScheme,
    RequestTLScheme,
    RequestTRateUScheme,
    RequestTRScheme,
)
from services.request.tenant_request_service import TenantRequestService
from utils.grid_fs.file import File

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

    params = await TenantRequestFilter.parse_query_params(req.query_params)
    service = TenantRequestService(tenant)
    return await service.get_request_list(
        query_list=params.query_list,
        offset=params.offset,
        limit=params.limit,
        sort=params.sort,
    )


@tenant_request_router.get(
    path="/{request_id}",
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
    path="/{request_id}/evaluate",
    status_code=status.HTTP_200_OK,
    response_model=RequestTRScheme,
)
async def evaluate_request(
    tenant: TenantDep,
    request_id: PydanticObjectId,
    scheme: RequestTRateUScheme,
):
    """
    Оценивание выполнения заявки жителем
    """

    service = TenantRequestService(tenant)
    return await service.rate_request(
        request_id=request_id,
        scheme=scheme,
    )


@tenant_request_router.post(
    path="/{request_id}/requester_attachment_files",
    status_code=status.HTTP_200_OK,
    response_model=list[File],
)
async def upload_requester_attachments(
    tenant: TenantDep,
    request_id: PydanticObjectId,
    files: list[UploadFile],
):
    """
    Загрузка файлов вложения жителем
    """

    service = TenantRequestService(tenant)
    return await service.upload_requester_attachments(
        request_id=request_id,
        files=files,
    )
