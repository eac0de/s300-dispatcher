"""
Модуль с моделью закешированного дома
"""

from collections.abc import Mapping
from datetime import datetime
from typing import Any

import pydantic_core
from beanie import PydanticObjectId
from client.s300.client import ClientS300
from pydantic import BaseModel, Field
from starlette import status

from errors import FailedDependencyError
from utils.document_cache import DocumentCache
from utils.request.constants import RequestMethod


class ServiceBindHS300S(BaseModel):
    """
    Модель привязок дома к организациям
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор привязки",
    )
    provider: PydanticObjectId = Field(
        title="Идентификатор организации",
    )
    business_type: PydanticObjectId = Field(
        title="Вид деятельности в отношении к дому",
    )
    start_at: datetime = Field(
        title="Время начала привязки",
    )
    end_at: datetime | None = Field(
        title="Время окончания привязки",
    )
    is_public: bool = Field(
        title="Эксплуатация МКД",
    )
    is_active: bool = Field(
        title="Эксплуатация МКД",
    )
    group: PydanticObjectId | None = Field(
        title="Время окончания привязки",
    )


class StandpipeHS300S(BaseModel):
    """
    Модель стояка подЪезда
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор стояка",
    )


class LiftHS300S(BaseModel):
    """
    Модель лифта подЪезда
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор лифта",
    )


class PorchHS300S(BaseModel):
    """
    Модель подЪезда дома
    """

    standpipes: list[StandpipeHS300S] = Field(
        default_factory=list,
        title="Стояки крыльца",
    )
    lifts: list[LiftHS300S] = Field(
        default_factory=list,
        title="Лифты крыльца",
    )


class SettingsHS300S(BaseModel):
    """
    Модель настроек дома
    """

    requests_provider: PydanticObjectId = Field(
        title="Идентификатор организации отвечающей за заявки",
    )


class HouseS300(DocumentCache):
    """
    Модель закешированного дома
    """

    address: str = Field(
        title="Адрес дома",
    )
    service_binds: list[ServiceBindHS300S] = Field(
        default_factory=list,
        title="Вид деятельности в отношении к дому",
    )
    porches: list[PorchHS300S] = Field(
        default_factory=list,
        title="Крыльца",
    )
    settings: SettingsHS300S = Field(
        title="настройки дома",
    )

    async def get_lift(self, lift_id: PydanticObjectId) -> LiftHS300S | None:
        """
        Получение лифта дома по его идентификатору

        Args:
            lift_id (PydanticObjectId): Идентификатор лифта

        Returns:
            Lift | None: Модель лифта либо None если его не существует в данном доме
        """

        for p in list(self.porches):
            for l in p.lifts:
                if l.id == lift_id:
                    return l

    async def get_standpipe(self, standpipe_id: PydanticObjectId) -> StandpipeHS300S | None:
        """
        Получение стояка дома по его идентификатору

        Args:
            standpipe_id (PydanticObjectId): Идентификатор стояка

        Returns:
            Standpipe | None: Модель стояка либо None если его не существует в данном доме
        """

        for p in list(self.porches):
            for sp in p.standpipes:
                if sp.id == standpipe_id:
                    return sp

    @classmethod
    async def load(
        cls,
        query: Mapping[str, Any],
    ):
        """
        Метод для подгрузки из S300 дома

        Args:
            query (Mapping[str, Any]): Параметры запроса

        Notes:
            Будет подгружен первый, соответствующий запросу дом
        """

        path = "houses/get/"
        status_code, data = await ClientS300.send_request(
            path=path,
            method=RequestMethod.GET,
            tag="load_house",
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
        if not isinstance(data, dict) or data.get("house") is None:
            raise FailedDependencyError(
                description="The data transmitted from the S300 does not contain an «house» key",
            )
        try:
            await cls(**data["house"]).save()
        except pydantic_core.ValidationError as e:
            raise FailedDependencyError(
                description="House data does not correspond to expected values",
                error=str(e),
            ) from e
