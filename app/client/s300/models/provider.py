"""
Модуль с моделью закешированной организации
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


class ProviderS300(DocumentCache):
    """
    Модель закешированной организации
    """

    name: str = Field(
        title="Название организации",
    )

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

        path = "providers/get/"
        status_code, data = await ClientS300.send_request(
            path=path,
            method=RequestMethod.GET,
            tag="load_provider",
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
        if not isinstance(data, dict) or data.get("provider") is None:
            raise FailedDependencyError(
                description="The data transmitted from the S300 does not contain an «provider» key",
            )
        try:
            await cls(**data["provider"]).save()
        except pydantic_core.ValidationError as e:
            raise FailedDependencyError(
                description="Provider data does not correspond to expected values",
                error=str(e),
            ) from e
