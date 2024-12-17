from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel


class AppealCategory(Document):
    id: PydanticObjectId = Field(
        default_factory=PydanticObjectId,
        alias="_id",
        description="MongoDB document ObjectID",
    )
    name: str = Field(
        title="Название категории",
    )
    description: str = Field(
        title="Описание категории",
    )
    provider_id: PydanticObjectId = Field(
        title="Идентификатор организации-владельца категории",
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
