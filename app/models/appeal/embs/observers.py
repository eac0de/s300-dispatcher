from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from models.appeal.embs.employee import DepartmentAS, EmployeeAS


class EmployeeObserverAS(EmployeeAS):
    """
    Класс стандартного сотрудника из обращения. AS = Appeal Scheme
    """

    id: PydanticObjectId = Field(
        alias="_id",
        title="Идентификатор связанной заявки",
    )
    full_name: str = Field(
        title="Фамилия Имя Отчество сотрудника",
    )


class ObserversAS(BaseModel):
    employees: list[EmployeeObserverAS] = Field(
        default_factory=list,
    )
    departments: list[DepartmentAS] = Field(
        default_factory=list,
    )
