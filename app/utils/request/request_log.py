"""
Модуль с моделью лога запроса
"""

from collections.abc import Mapping
from datetime import datetime

from beanie import Document
from pydantic import BaseModel, ConfigDict, Field


class ResponseInfo(BaseModel):
    """
    Класс информации об ответе
    """

    status: int = Field(title="Код ответа")
    headers: Mapping | None = Field(title="Заголовки ответа")
    body: Mapping | str | list | None = Field(title="Тело ответа")


class RequestInfo(BaseModel):
    """
    Класс информации о запросе
    """

    url: str = Field(
        title="URL запроса",
    )
    method: str = Field(
        title="Метод запроса",
    )
    headers: Mapping | None = Field(
        default=None,
        title="Заголовки запроса",
    )
    query_params: Mapping | None = Field(
        default=None,
        title="Параметры запроса",
    )
    body: Mapping | None = Field(
        default=None,
        title="Тело запроса",
    )


class RequestLog(Document):
    """
    Класс лога запроса
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    tag: str = Field(
        title="Тег запроса для отслеживания",
    )
    response_info: ResponseInfo | None = Field(
        default=None,
        title="Информация об ответе",
    )
    request_info: RequestInfo | None = Field(
        default=None,
        title="Информация о запросе",
    )
    error: str | None = Field(
        default=None,
        title="Ошибка запроса",
    )
    request_time: datetime = Field(
        default_factory=datetime.now,
        title="Время запроса",
    )
