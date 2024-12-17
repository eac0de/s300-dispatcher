from pydantic import Field

from models.base.binds import ProviderBinds
from models.base_document import BaseDocument


class OtherProvider(BaseDocument):
    """
    Модель сторонней организации
    """

    name: str = Field(
        title="Название сторонней организации",
    )
    inn: str = Field(
        pattern=r"\d{10}",
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
