from typing import Any

from elastic_transport import ObjectApiResponse
from elasticsearch import AsyncElasticsearch


class DocumentES:
    __es__: AsyncElasticsearch
    __es_index__: str

    @property
    async def es(self) -> AsyncElasticsearch:
        return self.__es__

    @classmethod
    async def init_es(cls, es: AsyncElasticsearch):
        cls.__es__ = es
        await cls.create_es_index()

    @classmethod
    async def create_es_index(cls):
        raise NotImplementedError(f"create_es_index of DocumentES not realized in {cls.__name__}")

    async def add_to_es(self):
        raise NotImplementedError(f"add_to_es of DocumentES not realized in {self.__class__.__name__}")

    async def update_to_es(self):
        raise NotImplementedError(f"update_to_es of DocumentES not realized in {self.__class__.__name__}")

    @classmethod
    async def es_search(cls, body: dict[str, Any]) -> ObjectApiResponse[Any]:
        return await cls.__es__.search(index=cls.__es_index__, body=body)  # Убираем возвращаемые документы
