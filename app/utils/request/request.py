"""
Модуль с функцией для отправки HTTP-запроса с логированием.

Данный модуль предоставляет функцию `send_request_with_log`, которая позволяет отправлять HTTP-запросы и автоматически создавать логи запросов и ответов.
"""

import asyncio
from collections.abc import Mapping
from typing import Any

import aiohttp

from errors import FailedDependencyError
from utils.request.constants import RequestMethod
from utils.request.request_log import RequestInfo, RequestLog, ResponseInfo


async def send_request_with_log(
    url: str,
    method: RequestMethod,
    tag: str,
    body: Mapping[str, Any] | None = None,
    query_params: Mapping[str, str | list[str] | set[str]] | None = None,
    headers: dict | None = None,
    req_json: bool = True,
    res_json: bool = True,
) -> tuple[int, str | dict[str, Any]]:
    """
    Отправляет HTTP-запрос и создает лог запроса и ответа.

    Args:
        url (str): URL для отправки запроса.
        method (RequestMethod): Метод HTTP-запроса (например, GET, POST).
        tag (str): Тег для логирования запроса, помогает идентифицировать запрос в логах.
        body (Mapping[str, Any], optional): Тело запроса. Если не указано, тело не будет отправлено.
        query_params (Mapping[str, str | list[str] | set[str]], optional): Параметры запроса, добавляемые к URL.
        headers (dict, optional): Заголовки запроса, передаваемые серверу.
        req_json (bool): Указывает, нужно ли отправлять тело запроса в формате JSON. По умолчанию True.
        res_json (bool): Указывает, нужно ли возвращать ответ в формате JSON. По умолчанию True.

    Returns:
        tuple[int, str | dict[str, Any]]: Статус код ответа и данные ответа. Если `res_json` True, то данные будут в формате dict.

    Raises:
        FailedDependencyError: Если возникла ошибка при отправке запроса или получении ответа.

    Example:
        >>> status_code, response = await send_request_with_log(
        ...     url='https://api.example.com/data',
        ...     method=RequestMethod.GET,
        ...     tag='example_request'
        ... )
        >>> print(status_code)
        200
        >>> print(response)
        {'key': 'value'}
    """
    status_code = 999
    error = None
    res_body = None
    request_info = RequestInfo(
        url=url,
        method=method,
        headers=headers,
        body=body,
        query_params=query_params,
    )
    response_info = None
    if query_params:
        url += "?"
        for key, value in query_params.items():
            if isinstance(value, (list, set)):
                for v in value:
                    url += f"{str(key)}={v}&"
            else:
                url += f"{str(key)}={value}&"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(
                method=method,
                url=url,
                headers=headers if headers else None,
                json=body if req_json and body else None,
                data=body if not req_json and body else None,
                timeout=aiohttp.ClientTimeout(5),
            ) as response:
                request_info.headers = response.request_info.headers
                status_code = response.status
                if res_json:
                    try:
                        res_body = await response.json()
                    except:
                        try:
                            res_body = await response.text()
                        except:
                            pass
                else:
                    try:
                        res_body = await response.text()
                    except:
                        pass
                response_info = ResponseInfo(
                    status=status_code,
                    headers=dict(response.headers),
                    body=res_body,
                )
        except aiohttp.ClientError as e:
            error = f"ClientError - {str(e)}"
        except asyncio.TimeoutError:
            error = "TimeoutError"
        except Exception as e:
            error = str(e)
        finally:
            rl = RequestLog(
                request_info=request_info,
                response_info=response_info,
                error=error,
                tag=tag,
            )
            rl = await rl.save()
            if error:
                raise FailedDependencyError(description=error, tag=tag, request_log_id=rl.id)
        return status_code, res_body  # type: ignore
