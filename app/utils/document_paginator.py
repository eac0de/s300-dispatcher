from typing import Generic, TypeVar

from beanie import Document
from beanie.odm.queries.find import FindMany
from pydantic import BaseModel

T = TypeVar("T", bound=Document)
B = TypeVar("B")


class DocumentPagination(BaseModel, Generic[T]):
    limit: int
    offset: int
    count: int 
    result: list[T]

    @classmethod
    async def from_find(cls, find: FindMany[T], limit: int, offset: int | None = None) -> "DocumentPagination[T]":
        if offset is None:
            offset = 0
        return cls(
            limit=limit,
            offset=offset,
            count=await find.count(),
            result=await find.skip(offset).limit(limit).to_list(),
        )
