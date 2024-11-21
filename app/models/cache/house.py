"""
Модуль с моделью закешированного дома
"""

from collections.abc import Mapping
from datetime import datetime
from typing import Any

import pydantic_core
from beanie import PydanticObjectId
from pydantic import BaseModel, Field
from starlette import status

from client.c300_client import ClientC300
from errors import FailedDependencyError
from utils.document_cache import DocumentCache
from utils.request.constants import RequestMethod


class ServiceBindHCS(BaseModel):
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


class StandpipeHCS(BaseModel):
    """
    Модель стояка подЪезда
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор стояка",
    )


class LiftHCS(BaseModel):
    """
    Модель лифта подЪезда
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор лифта",
    )


class PorchHCS(BaseModel):
    """
    Модель подЪезда дома
    """

    standpipes: list[StandpipeHCS] = Field(
        default_factory=list,
        title="Стояки крыльца",
    )
    lifts: list[LiftHCS] = Field(
        default_factory=list,
        title="Лифты крыльца",
    )


class SettingsHCS(BaseModel):
    """
    Модель настроек дома
    """

    requests_provider: PydanticObjectId = Field(
        title="Идентификатор организации отвечающей за заявки",
    )


class HouseCache(DocumentCache):
    """
    Модель закешированного дома
    """

    address: str = Field(
        title="Адрес дома",
    )
    service_binds: list[ServiceBindHCS] = Field(
        default_factory=list,
        title="Вид деятельности в отношении к дому",
    )
    porches: list[PorchHCS] = Field(
        default_factory=list,
        title="Крыльца",
    )
    settings: SettingsHCS = Field(
        title="настройки дома",
    )

    async def get_lift(self, lift_id: PydanticObjectId) -> LiftHCS | None:
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

    async def get_standpipe(self, standpipe_id: PydanticObjectId) -> StandpipeHCS | None:
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
        Метод для подгрузки из C300 дома

        Args:
            query (Mapping[str, Any]): Параметры запроса

        Notes:
            Будет подгружен первый, соответствующий запросу дом
        """

        path = "houses/get/"
        status_code, data = await ClientC300.send_request(
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
                description="Unsatisfactory response from C300",
                status_code=status_code,
                body=str(data)[:200],
            )
        if not isinstance(data, dict) or data.get("house") is None:
            raise FailedDependencyError(
                description="The data transmitted from the C300 does not contain an «house» key",
            )
        try:
            await cls(**data["house"]).save()
        except pydantic_core.ValidationError as e:
            raise FailedDependencyError(
                description="House data does not correspond to expected values",
                error=str(e),
            ) from e
