"""
Модуль с сервисом для работы с позициями каталога жителем
"""

from datetime import datetime
from typing import Any

from fastapi import HTTPException
from starlette import status

from models.cache.house import HouseCache
from models.cache.tenant import TenantCache
from models.catalog_item.catalog_item import CatalogItem


class TenantCatalogItemService:
    """
    Сервис для работы с позициями каталога жителем
    """

    def __init__(
        self,
        tenant: TenantCache,
    ):
        self.tenant = tenant

    async def get_catalog_item_groups(
        self,
    ) -> list[str]:
        """
        Получение групп позиций каталога

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            list[str]: Список групп позиций каталога
        """
        house = await HouseCache.get(self.tenant.house.id)
        if not house:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="House not found",
            )
        provider_id = house.settings.requests_provider
        if not provider_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There is no organization in your house that is responsible for requests",
            )
        current_time = datetime.now()
        query = {
            "provider_id": provider_id,
            "is_available": True,
            "available_from": {
                "$gt": current_time,
            },
            "available_until": {
                "$lt": current_time,
            },
        }
        catalog_item_groups = await CatalogItem.get_motor_collection().distinct("group", query)
        return catalog_item_groups

    async def get_catalog_items(
        self,
        query_list: list[dict[str, Any]],
        offset: int | None = None,
        limit: int | None = None,
        sort: list[str] | None = None,
    ) -> list[CatalogItem]:
        """
        Получение списка позиций каталога

        Args:
            query_list (list[dict[str, Any]]): Список словарей для составления запроса
            offset (int | None, optional): Количество пропускаемых документов. Defaults to None
            limit (int | None, optional): Количество документов. Defaults to None
            sort (list[str] | None, optional): Список полей для сортировки. Defaults to None

        Returns:
            list[CatalogItem]: Список позиций каталога
        """
        house = await HouseCache.get(self.tenant.house.id)
        if not house:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="House not found",
            )
        provider_id = house.settings.requests_provider
        if not provider_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There is no organization in your house that is responsible for requests",
            )
        current_time = datetime.now()
        query_list.append(
            {
                "provider_id": provider_id,
                "is_available": True,
                "available_from": {
                    "$gt": current_time,
                },
                "available_until": {
                    "$lt": current_time,
                },
            }
        )
        catalog_items = CatalogItem.find(*query_list)
        catalog_items.sort(*sort if sort else ["-_id"])
        catalog_items.skip(0 if offset is None else offset)
        catalog_items.limit(20 if limit is None else limit)
        return await catalog_items.to_list()
