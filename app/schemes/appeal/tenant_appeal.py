from pydantic import BaseModel, Field

from models.appeal.appeal import Appeal
from models.base.binds import DepartmentBinds


class AppealTRLScheme(Appeal):
    binds: DepartmentBinds = Field(
        alias="_binds",
        title="Привязки к организации и группе домов",
        exclude=True,
    )


class AppealTEvaluateUScheme(BaseModel):
    """
    Класс схемы заявки для обновления ее оценки выполнения жителем
    """

    evaluation: int = Field(
        default=0,
        ge=0,
        le=5,
        title="Оценка жителя",
    )
