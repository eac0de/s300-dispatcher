"""
Модуль с кастомными моделями для ответа на запрос.

Этот модуль определяет кастомный JSON-ответ для обработки типов `ObjectId` и `PydanticObjectId`,
используя кастомный энкодер JSON. Это позволяет корректно сериализовать объекты MongoDB при
возвращении их в ответах API.

Классы:
    - JSONResponse: Кастомный ответ FastAPI, обрабатывающий типы ObjectId.

Примечания:
    - Использование этого модуля упрощает интеграцию с базами данных MongoDB,
      предоставляя удобный способ сериализации данных для API-ответов.
"""

import json
import typing
from collections.abc import Mapping

from fastapi import Response
from starlette.background import BackgroundTask

from utils.json_encoders import ObjectIdEncoder


class JSONResponse(Response):
    """
    Класс кастомного ответа в JSON для обработки типов ObjectId.

    Этот класс наследует от `Response` FastAPI и переопределяет метод `render`
    для обеспечения сериализации объектов ObjectId. Это полезно при работе с
    данными MongoDB.

    Атрибуты:
        media_type (str): Тип контента ответа (по умолчанию "application/json").

    Методы:
        - render(content): Сериализует переданное содержимое в JSON с использованием
          кастомного энкодера ObjectIdEncoder.
    """

    media_type = "application/json"

    def __init__(
        self,
        content: typing.Any,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=ObjectIdEncoder,
        ).encode("utf-8")
