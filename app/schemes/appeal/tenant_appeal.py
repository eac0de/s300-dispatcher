from pydantic import Field

from models.appeal.appeal import Appeal
from models.base.binds import DepartmentBinds


class AppealTRLScheme(Appeal):
    binds: DepartmentBinds = Field(
        alias="_binds",
        title="Привязки к организации и группе домов",
        exclude=True,
    )
