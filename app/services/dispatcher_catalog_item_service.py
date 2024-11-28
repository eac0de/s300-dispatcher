"""
Модуль с сервисом для работы с позициями каталога сотрудником
"""

from datetime import datetime
from typing import Any

from beanie import PydanticObjectId
from beanie.exceptions import RevisionIdWasChanged
from fastapi import HTTPException, UploadFile
from starlette import status

from client.s300.api import S300API
from client.s300.models.employee import EmployeeS300
from models.catalog_item.catalog_item import CatalogItem
from schemes.catalog_item import CatalogItemCScheme, CatalogItemUScheme
from utils.grid_fs.constants import FileExtensionGroup
from utils.grid_fs.file import File

CATALOG_ITEM_IMAGE_FILE_TAG = "catalog_item_image"


class DispatcherCatalogItemService:
    """
    Класс сервиса для работы с позициями каталога сотрудником
    """

    def __init__(
        self,
        employee: EmployeeS300,
    ):
        """
        Инициализация сервиса

        Args:
            employee (EmployeeS300): Модель работника осуществляющего работу с позициями каталога
        """
        self.employee = employee

    @staticmethod
    async def get_current_price(
        catalog_item: CatalogItem,
    ) -> int:
        """
        Получения текущей стоимости

        Args:
            item (CatalogItem): Позиция каталога

        Returns:
            int: Текущая стоимость
        """
        current_time = datetime.now()

        sorted_price_list = sorted(catalog_item.prices, key=lambda x: x.start_at)
        for i, price in enumerate(sorted_price_list):
            if price.start_at <= current_time:
                if i == len(sorted_price_list) - 1 or sorted_price_list[i + 1].start_at > current_time:
                    return price.amount
        raise Exception(f"Catalog item {catalog_item.id} has not price")

    async def get_catalog_item_groups(
        self,
    ) -> list[str]:
        """
        Получение возможных групп позиций каталога

        Returns:
            list[str]: Список групп
        """
        query = {"provider_id": self.employee.provider.id}
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
        query_list.append({"provider_id": self.employee.provider.id})
        catalog_items = CatalogItem.find(*query_list)
        catalog_items.sort(*sort if sort else ["-_id"])
        catalog_items.skip(0 if offset is None else offset)
        catalog_items.limit(20 if limit is None else limit)
        return await catalog_items.to_list()

    @staticmethod
    async def _validate_catalog_item_scheme(scheme: CatalogItemCScheme | CatalogItemUScheme):
        if scheme.is_available:
            if not scheme.available_from:
                raise HTTPException(
                    detail="The 'available_from' date must be specified when the catalog item is available",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            if scheme.available_until and scheme.available_until < scheme.available_from:
                raise HTTPException(
                    detail="The 'available_until' date cannot be earlier than 'available_from' date for a catalog item",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            if not scheme.prices:
                raise HTTPException(
                    detail="A price must be specified when the catalog item is available",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            min_price_start_at = min(price.start_at for price in scheme.prices)
            if min_price_start_at > scheme.available_from:
                raise HTTPException(
                    detail="The earliest price start time cannot be later than the available_from time",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

    async def create_catalog_item(
        self,
        scheme: CatalogItemCScheme,
    ) -> CatalogItem:
        """
        Создание позиции каталога

        Args:
            scheme (CatalogItemCUScheme): Схема для создания позиции каталога

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            CatalogItem: Созданная позиция каталога
        """

        await self._validate_catalog_item_scheme(scheme)
        house_ids = await S300API.get_allowed_house_ids(
            provider_id=self.employee.provider.id,
            house_ids=scheme.house_ids,
            house_group_ids=scheme.house_group_ids,
            fias=scheme.fias,
        )
        catalog_item = CatalogItem(
            provider_id=self.employee.provider.id,
            house_ids=house_ids,
            **scheme.model_dump(by_alias=True, exclude={"house_ids", "house_group_ids", "fias"}),
        )
        try:
            catalog_item = await catalog_item.save()
        except RevisionIdWasChanged as e:
            raise HTTPException(
                detail="The catalog item name or code cannot be repeated",
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from e
        return catalog_item

    async def update_catalog_item(
        self,
        catalog_item_id: PydanticObjectId,
        scheme: CatalogItemUScheme,
    ) -> CatalogItem:
        """
        Обновление позиции каталога

        Args:
            catalog_item_id (PydanticObjectId): Идентификатор позиции каталога
            scheme (CatalogItemCUScheme): Схема для обновления позиции каталога

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            CatalogItem: Обновленная позиция каталога
        """
        existing_catalog_item = await self._get_catalog_item(catalog_item_id)
        current_time = datetime.now()
        scheme.prices = [price for price in existing_catalog_item.prices if price.start_at < current_time] + [price for price in scheme.prices if price.start_at > current_time]
        await self._validate_catalog_item_scheme(scheme)
        house_ids = existing_catalog_item.house_ids
        if scheme.house_ids != existing_catalog_item.house_ids or scheme.house_group_ids or scheme.fias:
            house_ids = await S300API.get_allowed_house_ids(
                house_ids=scheme.house_ids,
                provider_id=self.employee.provider.id,
                house_group_ids=scheme.house_group_ids,
                fias=scheme.fias,
            )
        catalog_item = CatalogItem(
            _id=existing_catalog_item.id,
            provider_id=existing_catalog_item.provider_id,
            house_ids=house_ids,
            **scheme.model_dump(by_alias=True, exclude={"image", "house_ids", "house_group_ids", "fias"}),
        )
        if scheme.image:
            catalog_item.image = existing_catalog_item.image
        try:
            catalog_item = await catalog_item.save()
        except RevisionIdWasChanged as e:
            raise HTTPException(
                detail="The catalog item name or code cannot be repeated",
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from e
        return catalog_item

    async def delete_catalog_item(
        self,
        catalog_item_id: PydanticObjectId,
    ):
        """
        Удаление позиции каталога

        Args:
            catalog_item_id (PydanticObjectId): Идентификатор позиции каталога
        """
        catalog_item = await self._get_catalog_item(catalog_item_id)
        await catalog_item.delete()

    async def _get_catalog_item(
        self,
        catalog_item_id: PydanticObjectId,
    ) -> CatalogItem:
        catalog_item = await CatalogItem.find_one(
            {
                "_id": catalog_item_id,
                "provider_id": self.employee.provider.id,
            }
        )
        if not catalog_item:
            raise HTTPException(
                detail="Catalog item not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return catalog_item

    async def upload_catalog_item_image(
        self,
        catalog_item_id: PydanticObjectId,
        file: UploadFile,
    ) -> CatalogItem:
        """
        Загрузка изображения позиции каталога

        Args:
            catalog_item_id (PydanticObjectId): Идентификатор позиции каталога
            file (UploadFile): Изображение

        Returns:
            CatalogItem: Обновленная позиция каталога
        """
        catalog_item = await self._get_catalog_item(catalog_item_id)
        f = await File.create(
            file_content=await file.read(),
            filename=file.filename,
            tag=CATALOG_ITEM_IMAGE_FILE_TAG,
            allowed_file_extensions=FileExtensionGroup.IMAGE,
        )
        if catalog_item.image:
            await catalog_item.image.delete()
        catalog_item.image = f
        await catalog_item.save()
        return catalog_item

    async def download_catalog_item_image(
        self,
        catalog_item_id: PydanticObjectId,
    ) -> File:
        """
        Скачивание файла изображения позиции каталога

        Args:
            catalog_item_id (PydanticObjectId): Идентификатор позиции каталога

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            File: Файл изображения позиции каталога
        """
        catalog_item = await self._get_catalog_item(catalog_item_id)
        if not catalog_item.image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )
        return catalog_item.image
