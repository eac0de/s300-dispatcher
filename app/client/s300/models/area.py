"""
Модуль с моделью закешированного помещения
"""

from collections.abc import Mapping
from typing import Any

import pydantic_core
from client.s300.client import ClientS300
from pydantic import Field
from starlette import status

from errors import FailedDependencyError
from utils.document_cache import DocumentCache
from utils.request.constants import RequestMethod


class AreaS300(DocumentCache):
    """
    Модель закешированного помещения
    """

    number: str = Field(
        title="Номер квартиры",
    )
    formatted_number: str = Field(
        title="Номер квартиры с приставкой и доп информацией",
    )

    @classmethod
    async def load(
        cls,
        query: Mapping[str, Any],
    ):
        """
        Метод для подгрузки из S300 помещения

        Args:
            query (Mapping[str, Any]): Параметры запроса

        Notes:
            Будет подгружено первое, соответствующий запросу помещение
        """

        path = "areas/get/"
        status_code, data = await ClientS300.send_request(
            path=path,
            method=RequestMethod.GET,
            tag="load_area",
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
        if not isinstance(data, dict) or data.get("area") is None:
            raise FailedDependencyError(
                description="The data transmitted from the S300 does not contain an «area» key",
            )
        try:
            await cls(**data["area"]).save()
        except pydantic_core.ValidationError as e:
            raise FailedDependencyError(
                description="Area data does not correspond to expected values",
                error=str(e),
            ) from e
