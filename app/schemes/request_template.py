"""
Модуль со схемами для создания и обновления шаблона заявки
"""

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from models.request.categories_tree import RequestCategory, RequestSubcategory
from models.request_template.constants import RequestTemplateType
from models.request_template.request_template import RequestTemplate


class RequestTemplateCUScheme(BaseModel):
    """
    Класс схемы для создания и обновления шаблона заявки
    """

    name: str = Field(
        title="Название шаблона",
    )
    category: RequestCategory | None = Field(
        title="Категория заявки",
    )
    subcategory: RequestSubcategory | None = Field(
        title="Подкатегория заявки",
    )
    type: RequestTemplateType = Field(
        alias="_type",
        title="Тип шаблона",
    )
    body: str = Field(
        title="Тело шаблона",
    )


class RequestTemplateRLScheme(RequestTemplate):
    provider_id: PydanticObjectId = Field(
        title="Идентификатор организации-владельца категории",
        exclude=True,
    )
