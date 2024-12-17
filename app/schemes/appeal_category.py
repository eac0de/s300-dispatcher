"""
Модуль со схемами для создания и обновления категории обращения
"""

from pydantic import BaseModel, Field


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
