"""
Модуль с роутером для работы с позициями каталога жителем
"""

from fastapi import APIRouter, Request
from starlette import status

from api.dependencies.auth import TenantDep
from api.qp_translators.catalog_qp_translator import TenantCatalogQPTranslator
from models.catalog_item.catalog_item import CatalogItem
from models.catalog_item.constants import CatalogItemGroup
from services.tenant_catalog_item_service import TenantCatalogItemService

tenant_catalog_item_router = APIRouter(
    tags=["tenant_catalog_items"],
)


@tenant_catalog_item_router.get(
    path="/groups/",
    status_code=status.HTTP_200_OK,
    response_model=list[CatalogItemGroup],
)
async def get_catalog_item_groups(
    tenant: TenantDep,
):
    """
    Получение возможных групп позиций каталога
    """

    service = TenantCatalogItemService(tenant)
    catalog_item_groups = await service.get_catalog_item_groups()
    return catalog_item_groups


@tenant_catalog_item_router.get(
    path="/",
    description="Получение возможных позиций каталога" + TenantCatalogQPTranslator.get_docs(),
    status_code=status.HTTP_200_OK,
    response_model=list[CatalogItem],
)
async def get_catalog_item_list(
    tenant: TenantDep,
    req: Request,
):
    """
    Получение возможных позиций каталога
    """

    params = await TenantCatalogQPTranslator.parse(req.query_params)
    service = TenantCatalogItemService(tenant)
    catalog_item_list = await service.get_catalog_items(
        query_list=params.query_list,
        offset=params.offset,
        limit=params.limit,
        sort=params.sort,
    )
    return catalog_item_list
