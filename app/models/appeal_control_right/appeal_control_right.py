from beanie import Document, PydanticObjectId
from pydantic import Field

from models.appeal_control_right.constants import AppealControlRightType


class AppealControlRight(Document):
    id: PydanticObjectId = Field(
        default_factory=PydanticObjectId,
        alias="_id",
        description="MongoDB document ObjectID",
    )
    employee_id: PydanticObjectId = Field(
        title="Идентификатор сотрудника",
    )
    type: AppealControlRightType = Field(
        alias="_type",
        title="Тип права",
    )
