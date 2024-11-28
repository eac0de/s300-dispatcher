"""
Модуль с классом с готовыми ручками для обращения к другим микросервисам S300
"""

from collections.abc import Iterable

import pydantic_core
from beanie import PydanticObjectId
from fastapi import HTTPException
from pydantic import UUID4, TypeAdapter
from starlette import status

from client.s300.client import ClientS300
from errors import FailedDependencyError
from models.request.embs.commerce import CatalogItemCommerceRS
from models.request.embs.resources import WarehouseResourcesRS
from utils.request.constants import RequestMethod


class S300API:
    """
    Класс с готовыми ручками для обращения к другим микросервисам S300
    """

    @staticmethod
    async def upsert_storage_docs_out(
        request_id: PydanticObjectId,
        provider_id: PydanticObjectId,
        warehouses: dict[str, dict[str, float]] | None = None,
        is_rollback: bool = False,
    ) -> list[WarehouseResourcesRS]:
        if warehouses is None:
            warehouses = {}
        tag = "upsert_storage_docs_out"
        path = "storage_docs_out/"
        body = {
            "request_id": str(request_id),
            "provider_id": str(provider_id),
            "warehouses": warehouses,
            "is_rollback": is_rollback,
        }
        status_code, data = await ClientS300.send_request(
            path=path,
            method=RequestMethod.PUT,
            tag=tag,
            body=body,
        )
        if status_code == 400:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=data,
            )
        if status_code != 200:
            raise FailedDependencyError(
                description=f"{tag}: Unsatisfactory response from S300",
                status_code=status_code,
                body=str(data)[:200],
            )
        if not isinstance(data, dict) or data.get("warehouses") is None:
            raise FailedDependencyError("The data sent from the S300 does not contain the warehouses key")
        try:
            ta = TypeAdapter(list[WarehouseResourcesRS])
            wl = ta.validate_python(data["warehouses"])
            return wl
        except pydantic_core.ValidationError as e:
            raise FailedDependencyError(
                description="WarehousesList data does not correspond to expected values",
                error=str(e),
            ) from e

    @staticmethod
    async def get_house_group_ids(
        house_id: PydanticObjectId,
        area_id: PydanticObjectId | None = None,
    ) -> set[PydanticObjectId]:
        """
        Запрос на получение идентификаторов групп домов

        Args:
            house_id (PydanticObjectId): Идентификатор дома
            area_id (PydanticObjectId): Идентификатор квартиры

        Returns:
            list[PydanticObjectId]: Список идентификаторов групп домов

        Notes:
            - Может вернуть ошибку в ходе отправки запроса
        """

        tag = "get_house_groups"
        path = "house_groups/get_ids/"
        query_params = {"house_id": str(house_id)}
        if area_id:
            query_params.update({"area_id": str(area_id)})
        status_code, data = await ClientS300.send_request(
            path=path,
            method=RequestMethod.GET,
            tag=tag,
            query_params=query_params,
        )
        if status_code != 200:
            raise FailedDependencyError(
                description=f"{tag}: Unsatisfactory response from S300",
                status_code=status_code,
                body=str(data)[:200],
            )
        if not isinstance(data, dict) or data.get("house_group_ids") is None:
            raise FailedDependencyError("The data sent from the S300 does not contain the house_groups key")
        try:

            ta = TypeAdapter(set[PydanticObjectId])
            house_group_ids = ta.validate_python(data["house_group_ids"])
            return house_group_ids
        except pydantic_core.ValidationError as e:
            raise FailedDependencyError(
                description="HouseGroupIds data does not correspond to expected values",
                error=str(e),
            ) from e

    @staticmethod
    async def get_allowed_worker_ids(
        employee_number: str,
        worker_ids: Iterable[PydanticObjectId],
    ) -> set[PydanticObjectId]:
        """
        Запрос на проверку доступных идентификаторов сотрудников

        Args:
            employee_number (str): Номер сотрудника от чего лица мы делаем запрос
            worker_ids (list[PydanticObjectId]): Список проверяемых идентификаторов сотрудников

        Returns:
            list[PydanticObjectId]: Список разрешенных идентификаторов сотрудников

        Notes:
            - Может вернуть ошибку в ходе отправки запроса
        """

        tag = "get_allowed_worker_ids"
        path = "workers/get_allowed_ids/"
        query_params = {
            "profile": employee_number,
            "ids": worker_ids,
        }
        status_code, data = await ClientS300.send_request(
            path=path,
            method=RequestMethod.GET,
            tag=tag,
            query_params=query_params,
        )
        if status_code != 200:
            raise FailedDependencyError(
                description=f"{tag}: Unsatisfactory response from S300",
                status_code=status_code,
                body=str(data)[:200],
            )
        if not isinstance(data, dict) or data.get("allowed_worker_ids") is None:
            raise FailedDependencyError(
                description="The data transmitted from the S300 does not contain an allowed_worker_ids key",
            )
        try:
            ta = TypeAdapter(set[PydanticObjectId])
            allowed_worker_ids = ta.validate_python(data["allowed_worker_ids"])
            return allowed_worker_ids
        except pydantic_core.ValidationError as e:
            raise FailedDependencyError(
                description="AllowedWorkerIds data does not correspond to expected values",
                error=str(e),
            ) from e

    @staticmethod
    async def get_allowed_house_ids(
        provider_id: PydanticObjectId,
        house_ids: set[PydanticObjectId] | None = None,
        house_group_ids: set[PydanticObjectId] | None = None,
        fias: set[UUID4] | None = None,
    ) -> set[PydanticObjectId]:
        result = set()
        if not house_ids and not house_group_ids and not fias:
            return result

        tag = "get_allowed_house_ids"
        path = "houses/get_allowed_ids/"
        query_params = {
            "provider_id": provider_id,
            "house_ids": house_ids if house_ids else [],
            "house_group_ids": house_group_ids if house_group_ids else [],
            "fias": fias if fias else [],
        }
        status_code, data = await ClientS300.send_request(
            path=path,
            method=RequestMethod.GET,
            tag=tag,
            query_params=query_params,
        )
        if status_code != 200:
            raise FailedDependencyError(
                description=f"{tag}: Unsatisfactory response from S300",
                status_code=status_code,
                body=str(data)[:200],
            )
        if not isinstance(data, dict) or data.get("allowed_house_ids") is None:
            raise FailedDependencyError(
                description="The data transmitted from the S300 does not contain an allowed_house_ids key",
            )
        try:
            ta = TypeAdapter(set[PydanticObjectId])
            allowed_house_ids = ta.validate_python(data["allowed_house_ids"])
            return allowed_house_ids
        except pydantic_core.ValidationError as e:
            raise FailedDependencyError(
                description="AllowedHouseIds data does not correspond to expected values",
                error=str(e),
            ) from e

    @staticmethod
    async def create_receipt_for_paid_request(
        request_id: PydanticObjectId,
        provider_id: PydanticObjectId,
        tenant_email: str | None,
        catalog_items: list[CatalogItemCommerceRS],
    ):
        """
        Запрос на создание чека для оплаченной заявки

        Args:
            request_id (PydanticObjectId): Идентификатор заявки
            provider_id (PydanticObjectId): Идентификатор организации
            tenant_email (str | None): Почта жителя
            catalog_items (list[CatalogItemCommerceRS]): Список заказанных позиций

        Notes:
            - Может вернуть ошибку в ходе отправки запроса
        """
        tag = "create_receipt_for_paid_request"
        path = "receipts/"
        body = {
            "request_id": request_id,
            "provider_id": provider_id,
            "tenant_email": tenant_email,
            "positions": [
                {
                    "price": ci.price,
                    "quantity": ci.quantity,
                    "name": ci.name,
                }
                for ci in catalog_items
            ],
        }
        status_code, data = await ClientS300.send_request(
            path=path,
            method=RequestMethod.POST,
            tag=tag,
            body=body,
        )
        if status_code != 200:
            raise FailedDependencyError(
                description=f"{tag}: Unsatisfactory response from S300",
                status_code=status_code,
                body=str(data)[:200],
            )
