"""
Модуль с дополнительным классом - оценкой выполненных по заявке работ, которые поставили жители
"""

from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class EvaluationRS(BaseModel):
    """
    Класс оценки выполненных по заявке работ
    """

    tenant_id: PydanticObjectId = Field(
        title="Идентификатор человека проставившего оценку",
    )
    score: int = Field(
        ge=1,
        le=5,
        title="Оценка выполнения заявки (от 1 до 5)",
    )
    rated_at: datetime = Field(
        default_factory=datetime.now,
        title="Дата и время выставления оценки",
    )
