from beanie import PydanticObjectId
from pydantic import Field

from models.appeal_control_right.constants import AppealControlRightType
from models.base_document import BaseDocument


class AppealControlRight(BaseDocument):
    employee_id: PydanticObjectId = Field(
        title="Идентификатор сотрудника",
    )
    type: AppealControlRightType = Field(
        alias="_type",
        title="Тип права",
    )
