from beanie import PydanticObjectId
from pydantic import Field
from pymongo import IndexModel

from models.base_document import BaseDocument


class AppealCategory(BaseDocument):
    name: str = Field(
        title="Название категории",
    )
    description: str = Field(
        title="Описание категории",
    )
    provider_id: PydanticObjectId = Field(
        title="Идентификатор организации-владельца категории",
    )

    class Settings:
        """
        Настройки модели позиции каталога
        """

        indexes = [
            IndexModel(
                keys=["provider_id", "name"],
                name="provider_id__name__idx",
                unique=True,
            ),
        ]
