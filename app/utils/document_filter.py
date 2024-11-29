"""
Модуль для фильтрации параметров запроса в FastAPI.

Этот модуль предоставляет функциональность для фильтрации параметров запросов, 
которые поступают в API, с помощью класса `DocumentFilter`. Он реализует систему фильтров 
для различных типов данных и позволяет легко парсить, валидировать и применять фильтры 
к параметрам запроса, таким как `limit`, `offset`, и `sort_by`. В дополнение к фильтрам 
возможности парсинга данных также поддерживают стандартные типы данных, включая `datetime` 
и `bool`.

Notes:
    - Использование этого модуля упрощает создание гибких и безопасных фильтров
      для API-запросов.
    - Модуль также поддерживает работу с перечислениями (Enum), которые могут быть использованы
      в фильтрах для более строгой типизации.
"""

from collections.abc import Callable, Iterable
from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel, Field
from starlette import status
from starlette.datastructures import QueryParams

T = TypeVar("T")


class Filter(BaseModel, Generic[T]):
    """
    Класс фильтра для параметров запроса.

    Этот класс позволяет создавать фильтры для параметров запроса в API. Он включает
    функции для парсинга значений, применения условий фильтрации и определения,
    является ли фильтр обязательным.

    Attrs:
        q_func (Callable[[T | list[T]], dict[str, Any]]): Функция для преобразования
            значений фильтра в словарь для запроса к базе данных.
        t_parser (Callable[[str], T | list[T]]): Функция для преобразования строки
            в нужный тип данных.
        many (bool): Если True, фильтр может принимать список значений.
        exclusions (list[str]): Список фильтров, которые исключают текущий фильтр.
        is_required (bool): Если True, фильтр обязателен.
        description (str | None): Описание фильтра.

    Example:
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
        title="Определяет, может ли фильтр принимать список значений",
    )
    exclusions: list[str] = Field(
        default_factory=list,
        title="Список ключей фильтров, которые исключают текущий фильтр",
    )
    is_required: bool = Field(
        default=False,
        title="Если фильтр обязателен",
    )
    description: str | None = Field(
        default=None,
        title="Описание фильтра",
    )


class FilterParams(BaseModel):
    """
    Модель результата парсинга параметров запроса.

    Этот класс используется для хранения информации о фильтрах, полученных
    из параметров запроса API. Он также включает информацию о сортировке,
    лимите и смещении (пагинации).

    Attrs:
        query_list (list[dict[str, Any]]): Список фильтров, полученных из параметров запроса.
        sort (list[str]): Список ключей сортировки, указанных в запросе.
        limit (int | None): Лимит на количество возвращаемых результатов.
        offset (int | None): Смещение для пагинации результатов.
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


class DocumentFilterMetaclass(type):
    """
    Метакласс для автоматического объединения фильтров родителя и наследника.

    Этот метакласс позволяет автоматически объединять фильтры из родительских классов
    с фильтрами, определенными в текущем классе. Он также создает строку документации
    для каждого фильтра.
    """

    def __new__(
        cls,
        name: str,
        bases: tuple,
        namespace: dict[str, Any],
    ):
        filters: dict[str, Filter] = {}
        required_filter_set: set[str] = set()
        for base in bases:
            if hasattr(base, "__filters__"):
                filters.update(getattr(base, "__filters__", {}).copy())
        filters.update(namespace.get("__filters__", {}))
        required_filter_set.update([n for n, f in namespace.get("__filters__", {}).items() if f.is_required])
        namespace["__filters__"] = filters
        namespace["__required_filter_set__"] = required_filter_set
        namespace["__docs__"] = ""
        if namespace["__filters__"]:

            def filter_info(f: Filter):
                """Функция для извлечения информации о фильтре."""
                type_info = f.__pydantic_generic_metadata__["args"][0]  # type: ignore
                if issubclass(type_info, Enum):  # Проверяем, является ли тип Enum
                    enum_values = ", ".join([e.value for e in type_info])  # Получаем имена всех значений Enum
                    type_info = f"{type_info.__bases__[0].__name__ }({enum_values})"
                else:
                    type_info = type_info.__name__
                return f"{f.description + '<br><br>' if f.description else ''}**ValueType:** {type_info}<br>**Many:** {f.many}<br>**Is Required:** {f.is_required}{'<br>**Exclusions:** ' + ', '.join(f.exclusions) if f.exclusions else ''}"

            namespace["__docs__"] = "<h2>Filters:</h2>" + "<br>".join(f"<br><h3>{n}</h3>{filter_info(f)}" for n, f in namespace["__filters__"].items())
        return super().__new__(cls, name, bases, namespace)


class DocumentFilter(metaclass=DocumentFilterMetaclass):
    """
    Класс для работы с фильтрами параметров запроса.

    Этот класс управляет фильтрами и обеспечивает парсинг параметров запроса в API.
    Фильтры определяются в классе с помощью поля `__filters__`.

    Attrs:
        __filters__ (dict[str, Filter[Any]]): Словарь фильтров, определенных в классе.
        __required_filter_set__ (set[str]): Множество обязательных фильтров.
        __docs__ (str): Строка документации для фильтров.

    Methods:
        parse_query_params(cls, query_params: QueryParams) -> FilterParams:
            Парсит параметры запроса и возвращает объект FilterParams.
        _check_required_filters(cls, existing_filters: Iterable[str]):
            Проверяет наличие всех обязательных фильтров.
        get_docs(cls) -> str:
            Возвращает строку документации для всех фильтров.
    """

    __filters__: dict[str, Filter[Any]] = {}
    __required_filter_set__: set[str] = set()
    __docs__: str = ""

    @classmethod
    async def parse_query_params(cls, query_params: QueryParams) -> FilterParams:
        """
        Метод для парсинга параметров запроса.

        Этот метод анализирует параметры запроса и возвращает результаты в виде
        объекта `FilterParams`.

        Args:
            query_params (QueryParams): Параметры запроса.

        Raises:
            HTTPException: В случае недопустимого запроса.

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
        query_params_keys = query_params.keys()
        for param in query_params_keys:
            if param in ["limit", "offset", "sort_by"] or param in query:
                continue
            f = cls.__filters__.get(param)
            if not f:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Some filters are not allowed",
                )
            for exclusion in f.exclusions:
                if exclusion in query_params_keys:
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
        await cls._check_required_filters(query.keys())
        filter_params.query_list = list(query.values())
        return filter_params

    @classmethod
    async def _check_required_filters(cls, existing_filters: Iterable[str]):
        """
        Проверяет наличие обязательных фильтров в запросе.

        Args:
            existing_filters (Iterable[str]): Существующие фильтры, переданные в запросе.

        Returns:
            HTTPException: Если обязательные фильтры не переданы.
        """
        if not cls.__required_filter_set__:
            return
        if undefined_required_filters := cls.__required_filter_set__ - set(existing_filters):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required filters: {', '.join(undefined_required_filters)}",
            )

    @classmethod
    def get_docs(cls) -> str:
        """
        Возвращает документацию для фильтров.

        Возвращает HTML-документацию для всех фильтров, определенных в классе.

        Returns:
            str: HTML-документация.
        """
        return cls.__docs__


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

    @staticmethod
    def get_enum_parser(enum: type[T]) -> Callable[[str], T]:
        """
        Метод для получения парсера для типовых значений Enum.

        Args:
            enum (Type[T]): Класс Enum, для которого требуется парсер.

        Returns:
            Callable[[str], T]: Парсер, который преобразует строку в элемент Enum.
        """

        def enum_parser(v: str) -> T:
            try:
                return enum(v)  # type: ignore
            except ValueError as e:
                enum_values = ", ".join([e.value for e in enum])  # type: ignore
                type_info = f"{enum.__bases__[0].__name__ }({enum_values})"
                raise ValueError(f"Value '{v}' is not a valid member of {type_info}") from e

        return enum_parser
