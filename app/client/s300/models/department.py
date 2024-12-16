"""
Модуль с моделью закешированной организации
"""

from collections.abc import Mapping
from typing import Any, Self

import pydantic_core
from beanie import PydanticObjectId
from pydantic import BaseModel, Field
from starlette import status

from client.s300.client import ClientS300
from errors import FailedDependencyError
from utils.document_cache import DocumentCache
from utils.request.constants import RequestMethod


class SettingsDepartmentS300(BaseModel):
    is_accepting_appeals: bool = Field(
        title="Прием обращений",
    )


class DepartmentS300(DocumentCache):
    """
    Модель закешированного отдела
    """

    name: str = Field(
        title="Название отдела",
    )
    settings: SettingsDepartmentS300 = Field(
        title="Настройки отдела",
    )
    provider_id: PydanticObjectId = Field(
        title="Идентификатор организации",
    )

    @classmethod
    async def get_by_is_accepting_appeals(
        cls,
        is_accepting_appeals: bool,
        provider_id: PydanticObjectId,
    ) -> Self | None:
        """
        Получение сотрудника с подгрузкой если его нет по его номеру

        Args:
            number (str): Номер сотрудника

        Returns:
            Self | None: Сотрудник, если есть. В другом случае None
        """

        document = await cls.find_one({"is_accepting_appeals": is_accepting_appeals, "provider_id": provider_id})
        if not document:
            await cls.load({"is_accepting_appeals": is_accepting_appeals, "provider_id": provider_id})
            document = await cls.find_one({"is_accepting_appeals": is_accepting_appeals, "provider_id": provider_id})
        return document

    @classmethod
    async def load(
        cls,
        query: Mapping[str, Any],
    ):
        """
        Метод для подгрузки из S300 организации

        Args:
            query (Mapping[str, Any]): Параметры запроса

        Notes:
            Будет подгружен первый, соответствующий запросу дом
        """

        path = "departments/get/"
        status_code, data = await ClientS300.send_request(
            path=path,
            method=RequestMethod.GET,
            tag="load_department",
            query_params=query,
            res_json=True,
        )
        if status_code == status.HTTP_404_NOT_FOUND:
            return
        if status_code != status.HTTP_200_OK:
            raise FailedDependencyError(
                description="Unsatisfactory response from S300",
                status_code=status_code,
                body=str(data)[:200],
            )
        if not isinstance(data, dict) or data.get("department") is None:
            raise FailedDependencyError(
                description="The data transmitted from the S300 does not contain an «department» key",
            )
        try:
            await cls(**data["department"]).save()
        except pydantic_core.ValidationError as e:
            raise FailedDependencyError(
                description="Department data does not correspond to expected values",
                error=str(e),
            ) from e
