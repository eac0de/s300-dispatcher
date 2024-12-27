"""
Модуль с моделью закешированного сотрудника
"""

from collections.abc import Mapping
from enum import Enum
from typing import Any, Self

import pydantic_core
from beanie import PydanticObjectId
from pydantic import BaseModel, Field
from starlette import status

from client.s300.client import ClientS300
from errors import FailedDependencyError
from models.extra.external_control import ExternalControl
from models.extra.phone_number import PhoneNumber
from utils.document_cache import DocumentCache
from utils.request.constants import RequestMethod


class AppealAccessLevel(str, Enum):
    ALL = "all"
    DEPARTMENT = "by_dept"
    BASIC = "basic"


class PositionES300S(BaseModel):
    """
    Модель должности сотрудника
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор должности",
    )
    name: str = Field(
        title="Название должности",
    )


class DepartmentES300S(BaseModel):
    """
    Модель отдела сотрудника
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор отдела",
    )
    name: str = Field(
        title="Название отдела",
    )


class ProviderES300S(BaseModel):
    """
    Модель организации сотрудника
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор организации",
    )
    name: str = Field(
        title="Название организации",
    )


class BindsPermissionsES300S(BaseModel):
    """
    Модель разрешений сотрудника
    """

    pr: PydanticObjectId = Field(
        title="Привязка к организации",
    )
    hg: PydanticObjectId = Field(
        title="Привязка к группе домов",
    )


class EmployeeS300(DocumentCache):
    """
    Модель закешированного сотрудника
    """

    short_name: str = Field(
        title="Фамилия И.О. сотрудника",
    )
    full_name: str = Field(
        title="Фамилия Имя Отчество сотрудника",
    )
    number: str = Field(
        title="Номер сотрудника",
    )
    phone_numbers: list[PhoneNumber] = Field(
        default_factory=list,
        title="Номера телефонов сотрудника",
    )
    email: str | None = Field(
        default=None,
        title="Email сотрудника",
    )
    position: PositionES300S = Field(
        title="Должность сотрудника",
    )
    department: DepartmentES300S = Field(
        title="Отдел сотрудника",
    )
    provider: ProviderES300S = Field(
        title="Организация сотрудника",
    )
    binds_permissions: BindsPermissionsES300S = Field(
        title="Доступ сотрудника",
    )
    external_control: ExternalControl | None = Field(
        exclude=True,
        default=None,
        title="Внешнее управление",
    )
    is_super: bool = Field(
        title="Суперпользователь",
    )
    appeal_access_level: AppealAccessLevel = Field(
        title="Права на контроль обращений",
    )

    @classmethod
    async def get_by_number(
        cls,
        number: str,
    ) -> Self | None:
        """
        Получение сотрудника с подгрузкой если его нет по его номеру

        Args:
            number (str): Номер сотрудника

        Returns:
            Self | None: Сотрудник, если есть. В другом случае None
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
        Метод для подгрузки из S300 сотрудника

        Args:
            query (Mapping[str, Any]): Параметры запроса

        Notes:
            Будет подгружен первый, соответствующий запросу сотрудник
        """

        path = "workers/get/"
        status_code, data = await ClientS300.send_request(
            path=path,
            method=RequestMethod.GET,
            tag="load_employee",
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
        if not isinstance(data, dict) or data.get("worker") is None:
            raise FailedDependencyError(
                description="The data transmitted from the S300 does not contain an «worker» key",
            )
        try:
            data = data["worker"]
            await cls(**data).save()
        except pydantic_core.ValidationError as e:
            raise FailedDependencyError(
                description="Worker data does not correspond to expected values",
                error=str(e),
            ) from e

    @property
    def s300_headers(self) -> dict[str, str]:
        return {
            "User-ID": str(self.id),
            "User-EC-ID": str(self.external_control.id) if self.external_control else "",
        }
