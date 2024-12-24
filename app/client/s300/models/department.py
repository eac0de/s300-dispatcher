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
from client.s300.models.employee import EmployeeS300
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
        employee: EmployeeS300,
    ) -> Self | None:

        document = await cls.find_one({"is_accepting_appeals": True, "provider_id": employee.provider.id})
        if document:
            return document
        path = "worker/departments/get_is_accepting_appeals/"
        status_code, data = await ClientS300.send_request(
            path=path,
            method=RequestMethod.GET,
            tag="load_department_by_is_accepting_appeals",
            headers={"User-ID": str(employee.id), "User-EC-ID": str(employee.external_control.id) if employee.external_control else ""},
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
            return await cls(**data["department"]).save()
        except pydantic_core.ValidationError as e:
            raise FailedDependencyError(
                description="Department data does not correspond to expected values",
                error=str(e),
            ) from e

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
