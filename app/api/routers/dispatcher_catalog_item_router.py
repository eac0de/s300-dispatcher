"""
Модуль с роутером для работы с позициями каталога для сотрудников
"""

from beanie import PydanticObjectId
from fastapi import APIRouter, Request, UploadFile
from fastapi.responses import StreamingResponse
from starlette import status

from api.dependencies.auth import EmployeeDep
from api.filters.catalog_filter import DispatcherCatalogFilter
from models.catalog_item.catalog_item import CatalogItem
from schemes.catalog_item import CatalogItemCScheme, CatalogItemUScheme
from services.dispatcher_catalog_item_service import DispatcherCatalogItemService

dispatcher_catalog_item_router = APIRouter(
    tags=["dispatcher_catalog_items"],
)


@dispatcher_catalog_item_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=list[CatalogItem],
)
async def get_catalog_items_list(
    employee: EmployeeDep,
    req: Request,
):
    """
    Получение списка позиций каталога работником.
    Для фильтрации есть определенные фильтры см. в модуле api/filters/catalog_filter
    """

    params = await DispatcherCatalogFilter.parse_query_params(req.query_params)
    service = DispatcherCatalogItemService(employee)
    catalog_item = await service.get_catalog_items(
        query_list=params.query_list,
        offset=params.offset,
        limit=params.limit,
        sort=params.sort,
    )
    return catalog_item


@dispatcher_catalog_item_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=CatalogItem,
)
async def create_catalog_item(
    employee: EmployeeDep,
    scheme: CatalogItemCScheme,
):
    """
    Создание позиции каталога работником
    """

    service = DispatcherCatalogItemService(employee)
    catalog_item = await service.create_catalog_item(scheme)
    return catalog_item


@dispatcher_catalog_item_router.get(
    path="/groups",
    status_code=status.HTTP_200_OK,
    response_model=list[str],
)
async def get_catalog_item_groups(
    employee: EmployeeDep,
):
    """
    Получение списка групп каталога работником
    """

    service = DispatcherCatalogItemService(employee)
    catalog_item_groups = await service.get_catalog_item_groups()
    return catalog_item_groups


@dispatcher_catalog_item_router.patch(
    path="/{catalog_item_id}",
    status_code=status.HTTP_200_OK,
    response_model=CatalogItem,
)
async def update_catalog_item(
    employee: EmployeeDep,
    catalog_item_id: PydanticObjectId,
    scheme: CatalogItemUScheme,
):
    """
    Обновление позиции каталога работником
    """
    service = DispatcherCatalogItemService(employee)
    catalog_item = await service.update_catalog_item(
        catalog_item_id=catalog_item_id,
        scheme=scheme,
    )
    return catalog_item


@dispatcher_catalog_item_router.delete(
    path="/{catalog_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_catalog_item(
    employee: EmployeeDep,
    catalog_item_id: PydanticObjectId,
):
    """
    Удаление позиции каталога работником
    """

    service = DispatcherCatalogItemService(employee)
    await service.delete_catalog_item(catalog_item_id)


@dispatcher_catalog_item_router.post(
    path="/{catalog_item_id}/image",
    status_code=status.HTTP_200_OK,
    response_model=CatalogItem,
)
async def upload_catalog_item_image(
    employee: EmployeeDep,
    catalog_item_id: PydanticObjectId,
    file: UploadFile,
):
    """
    Загрузка изображения позиции каталога работником
    """

    service = DispatcherCatalogItemService(employee)
    return await service.upload_catalog_item_image(
        catalog_item_id=catalog_item_id,
        file=file,
    )


@dispatcher_catalog_item_router.get(
    path="/{catalog_item_id}/image",
    status_code=status.HTTP_200_OK,
)
async def download_catalog_item_image(
    employee: EmployeeDep,
    catalog_item_id: PydanticObjectId,
):
    """
    Скачивание изображения позиции каталога работником
    """
    service = DispatcherCatalogItemService(employee)
    file = await service.download_catalog_item_image(catalog_item_id)
    response = StreamingResponse(await file.open_stream(), media_type=file.content_type)
    response.headers["Content-Disposition"] = f"attachment; filename={file.name}"
    return response
