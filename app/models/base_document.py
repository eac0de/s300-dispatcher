from beanie import Document, PydanticObjectId
from pydantic import Field


class BaseDocument(Document):
    id: PydanticObjectId = Field(
        default_factory=PydanticObjectId,
        alias="_id",
        description="MongoDB document ObjectID",
    )
    for_beanie_err: None = Field(
        default=None,
        exclude=True,
    )  # При наличии keep_nulls = False в Settings класса, если при сохранении нету полей которые = None, beanie выдает ошибку pymongo.errors.OperationFailure  # При наличии keep_nulls = False в Settings класса, если при сохранении нету полей которые = None, beanie выдает ошибку pymongo.errors.OperationFailure

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "Settings"):

            class Settings:
                keep_nulls = False

            cls.Settings = Settings
        else:
            settings = getattr(cls, "Settings")
            if not hasattr(settings, "keep_nulls"):
                settings.keep_nulls = False
                cls.Settings = settings
