"""
Модуль с клиентом к S300 для запросов к другим микросервисам
"""

import asyncio
from collections.abc import Mapping
from typing import Any

import aiohttp
from config import settings
from errors import FailedDependencyError
from utils.request.constants import RequestMethod
from utils.request.request import send_request_with_log


class ClientS300:
    """
    Класс клиента к S300 для запросов к другим микросервисам
    """

    __host: str | None = None

    @classmethod
    async def send_request(
        cls,
        path: str,
        method: RequestMethod,
        tag: str,
        body: Mapping[str, Any] | None = None,
        query_params: Mapping[str, Any | list[Any] | set[Any]] | None = None,
        headers: dict | None = None,
        req_json: bool = True,
        res_json: bool = True,
    ) -> tuple[int, str | dict[str, Any]]:
        """
        Функция для отправки запроса в S300, использует один и тот же хост для отправки, но если он недоступен переключается на другой

        Args:
            url (str): URL запроса
            method (RequestMethod): Метод запроса
            tag (str): Тег запроса
            body (dict[str, Any]): Тело запроса
            query_params (dict[str, str]): Параметры запроса
            headers (dict): Хедеры запроса
            req_json (bool): Тело запроса в формате JSON
            res_json (bool): Тело ответа в формате JSON

        Returns:
            tuple[int, str | dict[str, Any]]: Статус код и данные ответа
        """
        print(path)
        attempt = 0
        if not headers:
            headers = {}
        headers.update({"token": settings.S300_TOKEN})
        while True:
            url = f"{await cls.get_host()}/{settings.S300_API_PREFIX}/" + path
            try:
                return await send_request_with_log(
                    url=url,
                    method=method,
                    tag=tag,
                    body=body,
                    query_params=query_params,
                    headers=headers,
                    req_json=req_json,
                    res_json=res_json,
                )
            except:
                await cls.remove_host()
                if attempt >= 2:
                    raise
                attempt += 1

    @classmethod
    async def __is_host_alive(cls, url: str) -> bool:
        """
        Проверка хоста на жизнеспособность

        Args:
            url (str): Какой хост нужно проверить

        Returns:
            bool: Результат проверки
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    url=url,
                    timeout=aiohttp.ClientTimeout(total=10),
                ):
                    return True
            except aiohttp.ClientError:
                return False
            except asyncio.TimeoutError:
                return False

    @classmethod
    async def get_host(cls) -> str:
        """
        Получение жизнеспособного либо закешированного хоста

        Raises:
            FailedDependencyError: Если ни один хост не жизнеспособен

        Returns:
            str: Жизнеспособных хост
        """

        if cls.__host is None:
            for _ in range(2):
                for host in set(settings.S300_HOSTS):
                    if await cls.__is_host_alive(host):
                        cls.__host = host
                        return cls.__host
            raise FailedDependencyError("None of the S300 servers are available")
        return cls.__host

    @classmethod
    async def remove_host(cls):
        """
        Удаление закешированного хоста
        """

        cls.__host = None
