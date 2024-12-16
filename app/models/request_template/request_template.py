"""
Модуль с классом шаблона заявки
"""

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel

from models.request.categories_tree import RequestCategory, RequestSubcategory
from models.request_template.constants import RequestTemplateType


class RequestTemplate(Document):
    """
    Класс шаблона заявки
    """

    id: PydanticObjectId = Field(
        default_factory=PydanticObjectId,
        alias="_id",
        description="MongoDB document ObjectID",
    )
    provider_id: PydanticObjectId = Field(
        title="Идентификатор организации-владельца шаблона",
    )
    name: str = Field(
        title="Название шаблона",
    )
    category: RequestCategory | None = Field(
        default=None,
        title="Категория заявки",
    )
    subcategory: RequestSubcategory | None = Field(
        default=None,
        title="Подкатегория заявки",
    )
    type: RequestTemplateType = Field(
        alias="_type",
        title="Тип шаблона",
    )
    body: str = Field(
        title="Тело шаблона",
    )
    for_beanie_err: None = Field(
        default=None,
        exclude=True,
    )  # При наличии keep_nulls = False в Settings класса, если при сохранении нету полей которые = None, beanie выдает ошибку pymongo.errors.OperationFailure  # При наличии keep_nulls = False в Settings класса, если при сохранении нету полей которые = None, beanie выдает ошибку pymongo.errors.OperationFailure

    class Settings:
        """
        Настройки модели позиции каталога
        """

        keep_nulls = False
        indexes = [
            IndexModel(
                keys=["provider_id", "name"],
                name="provider_id__name__idx",
                unique=True,
            ),
        ]
