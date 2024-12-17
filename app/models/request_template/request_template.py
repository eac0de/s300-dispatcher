"""
Модуль с классом шаблона заявки
"""

from beanie import PydanticObjectId
from pydantic import Field
from pymongo import IndexModel

from models.base_document import BaseDocument
from models.request.categories_tree import RequestCategory, RequestSubcategory
from models.request_template.constants import RequestTemplateType


class RequestTemplate(BaseDocument):
    """
    Класс шаблона заявки
    """

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
