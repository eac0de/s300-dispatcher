"""
Модуль со схемами для создания и обновления категории обращения
"""

from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from models.appeal_category.appeal_category import AppealCategory


class AppealCategoryCUScheme(BaseModel):
    """
    Класс схемы для создания и обновления категории обращения
    """

    name: str = Field(
        title="Название категории",
    )
    description: str = Field(
        title="Описание категории",
    )


class AppealCategoryRLScheme(AppealCategory):

    provider_id: PydanticObjectId = Field(
        title="Идентификатор организации-владельца категории",
        exclude=True,
    )
