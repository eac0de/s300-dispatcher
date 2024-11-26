"""
Модуль с классом для фильтрации параметров запроса.

Этот модуль содержит классы и методы, которые позволяют фильтровать параметры
запроса в FastAPI. Он реализует возможность создания фильтров для различных
параметров, таких как `limit`, `offset`, и предоставляет возможность их
парсинга и валидации.

Классы:
    - Filter: Класс для определения фильтров.
    - FilterParams: Модель для хранения результатов парсинга параметров запроса.
    - DocumentFilter: Класс для обработки и парсинга параметров запроса.
    - StandartParser: Статический класс для парсинга стандартных типов данных.

Примечания:
    - Использование этого модуля упрощает создание гибких и безопасных фильтров
      для API-запросов.
"""

from collections.abc import Callable
from datetime import datetime
from typing import Any, Generic, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel, Field
from starlette import status
from starlette.datastructures import QueryParams

T = TypeVar("T")


class Filter(BaseModel, Generic[T]):
    """
    Класс фильтра для определения параметров фильтрации.

    Добавляется в поле __filters__ класса DocumentFilter.

    Пример использования:

        Создание фильтра для работы с фильтрами заявок:

        class RequestFilter(DocumentFilter):
            __filters__ = {
                "provider_id": Filter[PydanticObjectId](
                    q_func=lambda x: {"provider_id": x},
                    t_parser=StandartParser.get_type_parser(PydanticObjectId),
                    many=True,
                    exclusions=["position_id"],
                ),
            }
    """

    q_func: Callable[[T | list[T]], dict[str, Any]] = Field(
        title="Функция, возвращающая словарь для запроса к базе данных",
    )
    t_parser: Callable[[str], T | list[T]] = Field(
        default=lambda x: x,
        title="Функция для преобразования строки в нужный тип данных",
    )
    many: bool = Field(
        default=False,
        title="НОпределяет, может ли фильтр принимать список значений",
    )
    exclusions: list[str] = Field(
        default_factory=list,
        title="Список ключей фильтров, которые исключают текущий фильтр",
    )


class FilterParams(BaseModel):
    """
    Модель результата парсинга параметров запроса.
    """

    query_list: list[dict[str, Any]] = Field(
        default_factory=list,
        title="Список фильтров, полученных из параметров запроса",
    )
    sort: list[str] = Field(
        default_factory=list,
        title="Ключи сортировки, указанные в запросе",
    )
    limit: int | None = Field(
        default=None,
        title="Лимит на количество возвращаемых результатов",
    )
    offset: int | None = Field(
        default=None,
        title="Смещение для пагинации результатов",
    )


class DocumentFilter:
    """
    Класс для работы с фильтрами.

    Этот класс управляет фильтрами и обеспечивает парсинг параметров запроса.
    Фильтры определяются в классе с помощью поля __filters__.
    """

    __filters__: dict[str, Filter[Any]] = {}

    @classmethod
    async def parse_query_params(cls, query_params: QueryParams) -> FilterParams:
        """
        Метод для парсинга параметров запроса.

        Args:
            query_params (QueryParams): Параметры запроса.

        Raises:
            HTTPException: При неудовлетворительном запросе.

        Returns:
            FilterParams: Результат парсинга параметров запроса.
        """
        limit = query_params.get("limit")
        offset = query_params.get("offset")
        filter_params = FilterParams(
            limit=int(limit) if limit and limit.isdigit() else None,
            offset=int(offset) if offset and offset.isdigit() else None,
            sort=query_params.getlist("sort_by"),
        )
        query: dict[str, dict[str, Any]] = {}
        for param in query_params.keys():
            if param in ["limit", "offset", "sort_by"] or param in query:
                continue
            f = cls.__filters__.get(param)
            if not f:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Some filters are not allowed",
                )
            for exclusion in f.exclusions:
                if exclusion in query_params.keys():
                    query[param] = {}
                    break
            else:
                try:
                    if f.many:
                        value = [f.t_parser(p) for p in query_params.getlist(param)]
                    else:
                        value = f.t_parser(query_params.get(param))  # type: ignore
                except ValueError as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=str(e),
                    ) from e
                query[param] = f.q_func(value)
        filter_params.query_list = list(query.values())
        return filter_params


class StandartParser:
    """
    Стандартный парсер строк.

    Этот класс содержит статические методы для парсинга стандартных типов данных,
    таких как `datetime` и `bool`.
    """

    @staticmethod
    def datetime_parser(v: str) -> datetime:
        """
        Парсер даты и времени.

        Args:
            v (str): Дата и время в ISO формате.

        Raises:
            ValueError: При неверном формате даты и времени.

        Returns:
            datetime: Результат парсинга.
        """
        try:
            return datetime.fromisoformat(v)
        except Exception as e:
            raise ValueError("Field with date must be in ISO format") from e

    @staticmethod
    def bool_parser(v: str) -> bool:
        """
        Парсер булевых значений.

        Args:
            v (str): 'false' или 'true' в строковом формате.

        Raises:
            ValueError: При неверном формате булевого значения.

        Returns:
            bool: Результат парсинга.
        """
        if v not in ["false", "true"]:
            raise ValueError("Field with bool must be 'false' or 'true'")
        return v != "false"

    @staticmethod
    def get_type_parser(_type: type[T]) -> Callable[[str], T]:
        """
        Метод для получения парсера для типовых значений.

        Args:
            _type (type[T]): Тип, для которого требуется парсер.

        Returns:
            Callable[[str], T]: Парсер, который преобразует строку в указанный тип.
        """

        def type_parser(v: str) -> T:
            try:
                return _type(v)  # type: ignore
            except Exception as e:
                raise ValueError(f"Value {v} is not correct for type {_type.__name__}") from e

        return type_parser
