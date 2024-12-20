"""
Модуль с сервисами для работы с заявками для жителей
"""

import math
from datetime import datetime
from typing import Any

from beanie import PydanticObjectId
from fastapi import HTTPException, UploadFile
from file_manager import File
from starlette import status

from client.s300.models.area import AreaS300
from client.s300.models.house import HouseS300
from client.s300.models.provider import ProviderS300
from client.s300.models.tenant import TenantS300
from models.catalog_item.catalog_item import CatalogItem
from models.request.categories_tree import RequestCategory, RequestSubcategory
from models.request.constants import (
    RequestPayStatus,
    RequestSource,
    RequestStatus,
    RequestType,
)
from models.request.embs.area import AreaRS
from models.request.embs.commerce import CatalogItemCommerceRS, CommerceRS
from models.request.embs.employee import ProviderRS
from models.request.embs.execution import ExecutionRS, RateRS
from models.request.embs.house import HouseRS
from models.request.embs.requester import RequesterType, TenantRequester
from models.request.request import RequestModel
from schemes.request.tenant_request import (
    CatalogItemCommerceRequestTCatalogCScheme,
    RequestTCatalogCScheme,
    RequestTCScheme,
)
from services.dispatcher_catalog_item_service import DispatcherCatalogItemService
from services.request.request_service import RequestService


class TenantRequestService(RequestService):
    """
    Сервис для работы с заявками для жителей

    Args:
        RequestService (_type_): Сервис работы с заявками не привязанный к пользователю
    """

    def __init__(self, tenant: TenantS300):
        """
        Инициализация сервиса

        Args:
            tenant (TenantS300): Модель жителя осуществляющего работу с заявками
        """
        super().__init__()
        self.tenant = tenant

    async def get_request_list(
        self,
        query_list: list[dict[str, Any]],
        offset: int | None = None,
        limit: int | None = None,
        sort: list[str] | None = None,
    ) -> list[RequestModel]:
        """
        Получение списка заявок

        Args:
            query_list (list[dict[str, Any]]): Список словарей для составления запроса
            offset (int | None, optional): Количество пропускаемых документов. Defaults to None
            limit (int | None, optional): Количество документов. Defaults to None
            sort (list[str] | None, optional): Список полей для сортировки. Defaults to None

        Returns:
            list[RequestModel]: Список заявок
        """
        query_list.append(
            {
                "$or": [
                    {
                        "requester._id": self.tenant.id,
                        "requester._type": RequesterType.TENANT,
                    },
                    {
                        "house._id": self.tenant.house.id,
                        "is_public": True,
                    },
                ]
            }
        )
        requests = RequestModel.find(*query_list)
        requests.sort(*sort if sort else ["-_id"])
        requests.skip(0 if offset is None else offset)
        requests.limit(20 if limit is None else limit)
        result = []
        async for request in requests:
            request.execution.rates = await self._get_request_rates(request)
            result.append(request)
        return result

    async def get_request(
        self,
        request_id: PydanticObjectId,
    ) -> RequestModel:
        """
        Получение заявки

        Args:
            request_id (PydanticObjectId): Идентификатор заявки

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            RequestModel: Заявка
        """
        request = await self._get_request(request_id)
        request.execution.rates = await self._get_request_rates(request)
        return request

    async def _get_request(
        self,
        request_id: PydanticObjectId,
    ) -> RequestModel:
        query = {
            "_id": request_id,
            "$or": [
                {
                    "requester._id": self.tenant.id,
                    "requester._type": RequesterType.TENANT,
                },
                {
                    "house._id": self.tenant.house.id,
                    "is_public": True,
                },
            ],
        }
        request = await RequestModel.find_one(query)
        if not request:
            raise HTTPException(
                detail="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return request

    async def _get_request_rates(
        self,
        request: RequestModel,
    ) -> list[RateRS]:
        for e in request.execution.rates:
            if e.tenant_id == self.tenant.id:
                return [e]
        return []

    async def create_request(
        self,
        scheme: RequestTCScheme,
    ) -> RequestModel:
        """
        Создание заявки в свободной форме

        Args:
            scheme (RequestTCScheme): Схема для создания заявки

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            RequestModel: Созданная заявка
        """
        house = await HouseS300.get(self.tenant.house.id)
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
        provider = await ProviderS300.get(provider_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Request-provider from house not found",
            )

        area = None
        if scheme.type == RequestType.AREA:
            area = await AreaS300.get(self.tenant.area.id)
            if not area:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Area not found",
                )
        binds = await self._get_binds(
            house=house,
            provider_id=provider.id,
            execution_provider_id=provider.id,
            area_id=area.id if area else None,
        )
        number = await self._generate_number()
        provider_rs = ProviderRS.model_validate(provider.model_dump(by_alias=True))
        execution = ExecutionRS(
            desired_start_at=scheme.execution.desired_start_at,
            desired_end_at=scheme.execution.desired_end_at,
            provider=provider_rs,
        )
        house_rs = HouseRS.model_validate(house.model_dump(by_alias=True))
        tenant_requester = TenantRequester.model_validate(self.tenant.model_dump(by_alias=True))
        area_rs = AreaRS.model_validate(area.model_dump(by_alias=True)) if area else None
        request = RequestModel(
            _type=scheme.type,
            area=area_rs,
            house=house_rs,
            number=number,
            requester=tenant_requester,
            description=scheme.description,
            category=RequestCategory.BUILDING_RENOVATION,
            subcategory=RequestSubcategory.GENERAL_PROPERTY,
            provider=provider_rs,
            execution=execution,
            is_public=False,
            _binds=binds,
            source=RequestSource.TENANT,
        )
        return await request.save()

    async def create_catalog_request(
        self,
        scheme: RequestTCatalogCScheme,
    ) -> RequestModel:
        """
        Создание заявки из каталога

        Args:
            scheme (RequestTCatalogCScheme): Схема для создания заявки

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            RequestModel: Созданная заявка
        """
        if not scheme.commerce.catalog_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least 1 position is required",
            )
        house = await HouseS300.get(self.tenant.house.id)
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
        provider = await ProviderS300.get(provider_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Request-provider from house not found",
            )
        area = await AreaS300.get(self.tenant.area.id)
        if not area:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Area not found",
            )

        catalog_items = await self._get_catalog_items(
            commerce_catalog_items=scheme.commerce.catalog_items,
            provider_id=provider.id,
        )
        commerce = CommerceRS(
            pay_status=RequestPayStatus.WAIT,
            catalog_items=catalog_items,
        )
        binds = await self._get_binds(
            house=house,
            provider_id=provider.id,
            execution_provider_id=provider.id,
            area_id=area.id if area else None,
        )
        number = await self._generate_number()
        provider_rs = ProviderRS.model_validate(provider.model_dump(by_alias=True))
        execution = ExecutionRS(
            provider=provider_rs,
        )
        house_rs = HouseRS.model_validate(house.model_dump(by_alias=True))
        tenant_requester = TenantRequester.model_validate(self.tenant.model_dump(by_alias=True))
        area_rs = AreaRS.model_validate(area.model_dump(by_alias=True)) if area else None

        request = RequestModel(
            status=RequestStatus.HIDDEN,
            _type=RequestType.AREA,
            area=area_rs,
            house=house_rs,
            number=number,
            requester=tenant_requester,
            description=scheme.description if scheme.description else "Заказ позиций из каталога",
            category=RequestCategory.COMMERCIAL,
            subcategory=RequestSubcategory.CHARGEABLE,
            provider=provider_rs,
            execution=execution,
            is_public=False,
            commerce=commerce,
            _binds=binds,
            source=RequestSource.CATALOG,
        )
        return await request.save()

    async def _get_catalog_items(
        self,
        commerce_catalog_items: list[CatalogItemCommerceRequestTCatalogCScheme],
        provider_id: PydanticObjectId,
    ) -> list[CatalogItemCommerceRS]:
        commerce_catalog_items_map = {i.id: i.quantity for i in commerce_catalog_items}
        items = await CatalogItem.find(
            {
                "_id": {"$in": commerce_catalog_items_map.keys()},
                "provider_id": provider_id,
            },
        ).to_list()
        if len(commerce_catalog_items_map) != len(items):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not all positions were found at the provider",
            )
        catalog_items = []
        current_time = datetime.now()
        for i in items:
            if not i.is_available or current_time < i.available_from or (i.available_until and current_time > i.available_until):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Catalog item is not available",
                )
            price = await DispatcherCatalogItemService.get_current_price(i)
            quantity = float(math.ceil(commerce_catalog_items_map[i.id])) if i.is_divisible else commerce_catalog_items_map[i.id]
            catalog_items.append(
                CatalogItemCommerceRS(
                    _id=i.id,
                    name=i.name,
                    price=price,
                    quantity=quantity,
                )
            )
        return catalog_items

    async def rate_request(
        self,
        request_id: PydanticObjectId,
        score: int,
    ) -> RequestModel:
        """
        Оценка выполнения заявки

        Args:
            request_id (PydanticObjectId): Идентификатор заявки
            score (int): Схема для проставления оценки

        Raises:
            HTTPException: _description_

        Returns:
            RequestModel: _description_
        """
        request = await self._get_request(request_id)
        if request.status != RequestStatus.PERFORMED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request can only be rated once it has been performed",
            )

        existing_rate = next((e for e in request.execution.rates if e.tenant_id == self.tenant.id), None)
        if existing_rate:
            if score > 0:
                existing_rate.score = score
            else:
                request.execution.rates.remove(existing_rate)
        else:
            request.execution.rates.append(
                RateRS(
                    tenant_id=self.tenant.id,
                    score=score,
                )
            )
        request.execution.average_rating = (sum(e.score for e in request.execution.rates) / len(request.execution.rates)) if request.execution.rates else 0
        return await request.save()

    async def upload_requester_attachments(
        self,
        request_id: PydanticObjectId,
        files: list[UploadFile],
    ) -> list[File]:
        """
        Загрузка файлов вложения заявителя

        Args:
            files (list[UploadFile]): Файлы

        Raises:
            HTTPException: При неудовлетворительном запросе

        Returns:
            RequestModel: Обновленная заявка
        """
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Files is required",
            )
        request = await self._get_request(request_id)
        if self.tenant.id != request.requester.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the tenant who created the request can add requester attachments",
            )
        try:
            for file in files:
                f = await File.create(
                    file_content=await file.read(),
                    filename=file.filename if file.filename else "Unknown",
                    tag=await self.get_filetag_for_requester_attachment(request.id),
                )
                request.requester_attachment.files.append(f)
        except:
            for f in request.requester_attachment.files:
                await f.delete()
            raise
        await request.save()
        return request.requester_attachment.files
