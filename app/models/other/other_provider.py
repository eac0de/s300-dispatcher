from beanie import Document, PydanticObjectId
from pydantic import Field

from models.base.binds import ProviderBinds


class OtherProvider(Document):
    """
    Модель сторонней организации
    """

    id: PydanticObjectId = Field(
        default_factory=PydanticObjectId,
        alias="_id",
        description="MongoDB document ObjectID",
    )
    name: str = Field(
        title="Название сторонней организации",
    )
    inn: str = Field(
        pattern=r"\d{12}",
        title="ИНН сторонней организации",
    )
    ogrn: str = Field(
        pattern=r"\d{13}",
        title="ОГРН сторонней организации",
    )
    binds: ProviderBinds = Field(
        alias="_binds",
        title="Привязки к организации и группе домов",
    )
