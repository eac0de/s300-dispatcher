"""
Модуль с моделью закешированного жителя

TCS = Tenant Cache Scheme (Схема для модели закешированного жителя)
"""

from collections.abc import Mapping
from typing import Any

import pydantic_core
from beanie import PydanticObjectId
from pydantic import BaseModel, Field
from starlette import status

from client.c300.client import ClientC300
from errors import FailedDependencyError
from models.extra.phone_number import PhoneNumber
from utils.document_cache import DocumentCache
from utils.request.constants import RequestMethod


class HouseTC300S(BaseModel):
    """
    Модель дома жителя
    """

    id: PydanticObjectId = Field(
        alias="_id",
        description="MongoDB document ObjectID",
    )
    address: str = Field(
        title="Адрес дома",
    )


class AreaTC300S(BaseModel):
    """
    Модель помещения жителя
    """

    id: PydanticObjectId = Field(  # type: ignore
        alias="_id",
        description="MongoDB document ObjectID",
    )
    number: str = Field(
        title="Номер квартиры",
    )
    formatted_number: str = Field(
        title="Номер квартиры с приставкой и доп информацией",
    )


class TenantC300(DocumentCache):
    """
    Модель закешированного жителя
    """

    short_name: str = Field(
        title="Фамилия И.О. лица",
    )
    full_name: str = Field(
        title="Фамилия Имя Отчество жителя",
    )
    number: str = Field(
        title="Номер лицевого счета жителя",
    )
    phone_numbers: list[PhoneNumber] = Field(
        default_factory=list,
        title="Номера телефонов жителя",
    )
    email: str | None = Field(
        default=None,
        title="Email жителя",
    )
    area: AreaTC300S = Field(
        title="Квартира жителя",
    )
    house: HouseTC300S = Field(
        title="Дом жителя",
    )

    @classmethod
    async def get_by_number(
        cls,
        number: str,
    ):
        """
        Получение  жителя с подгрузкой если его нет по его номеру

        Args:
            number (str): Номер жителя

        Returns:
            Self | None: Житель, если есть. В другом случае None
        """

        document = await cls.find_one({"number": number})
        if not document:
            await cls.load({"number": number})
            document = await cls.find_one({"number": number})
        return document

    @classmethod
    async def load(
        cls,
        query: Mapping[str, Any],
    ):
        """
        Метод для подгрузки из C300 жителя

        Args:
            query (Mapping[str, Any]): Параметры запроса

        Notes:
            Будет подгружен первый, соответствующий запросу житель
        """

        path = "tenants/get/"
        status_code, data = await ClientC300.send_request(
            path=path,
            method=RequestMethod.GET,
            tag="load_tenant",
            query_params=query,
            res_json=True,
        )
        if status_code == status.HTTP_404_NOT_FOUND:
            return
        if status_code != status.HTTP_200_OK:
            raise FailedDependencyError(
                description="Unsatisfactory response from C300",
                status_code=status_code,
                body=str(data)[:200],
            )
        if not isinstance(data, dict) or data.get("tenant") is None:
            raise FailedDependencyError(
                description="The data transmitted from the C300 does not contain an «tenant» key",
            )
        try:
            await cls(**data["tenant"]).save()
        except pydantic_core.ValidationError as e:
            raise FailedDependencyError(
                description="Tenant data does not correspond to expected values",
                error=str(e),
            ) from e
