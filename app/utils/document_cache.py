"""
Модуль с моделью закешированного документа.

Этот модуль содержит класс `DocumentCache`, который представляет собой модель
документа, хранящегося в другой базе данных, управляемой другим микросервисом. Он
позволяет извлекать и загружать документы, используя асинхронный интерфейс.

Классы:
    - DocumentCache: Модель закешированного документа.
"""

from collections.abc import Mapping
from typing import Any, Self

from beanie import Document, PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorClientSession
from pydantic import Field


class DocumentCache(Document):
    """
    Модель закешированного документа.

    Этот класс используется для работы с документами, которые хранятся в
    другой базе данных, управляемой другим микросервисом.
    """

    id: PydanticObjectId = Field(  # type: ignore
        alias="_id",
        description="MongoDB document ObjectID",
    )

    @classmethod
    async def get(
        cls,
        document_id: Any,
        session: AsyncIOMotorClientSession | None = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
        with_children: bool = False,
        nesting_depth: int | None = None,
        nesting_depths_per_field: dict[str, int] | None = None,
        **pymongo_kwargs,
    ) -> Self | None:
        document = await super().get(
            document_id=document_id,
            session=session,
            ignore_cache=ignore_cache,
            fetch_links=fetch_links,
            with_children=with_children,
            nesting_depth=nesting_depth,
            nesting_depths_per_field=nesting_depths_per_field,
            **pymongo_kwargs,
        )
        if not document:
            await cls.load({"_id": document_id})
            document = await super().get(
                document_id=document_id,
                session=session,
                ignore_cache=ignore_cache,
                fetch_links=fetch_links,
                with_children=with_children,
                nesting_depth=nesting_depth,
                nesting_depths_per_field=nesting_depths_per_field,
                **pymongo_kwargs,
            )
        return document

    @classmethod
    async def load(
        cls,
        query: Mapping[str, Any],
    ):
        """
        Загрузка документа из другой базы данных микросервиса.

        Этот метод должен быть реализован в подклассе для загрузки документа
        из внешнего источника.

        Args:
            query (Mapping[str, Any]): Параметры запроса для получения документа.

        Raises:
            NotImplementedError: Если метод не реализован в подклассе.
        """
        raise NotImplementedError(f"func load not implemented for {cls.__name__}")
