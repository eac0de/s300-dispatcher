"""
Модуль с дополнительным классом - оценкой выполненных по заявке работ, которые поставили жители
"""

from datetime import datetime

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class RateRS(BaseModel):
    """
    Класс оценки выполненных по заявке работ
    """

    tenant_id: PydanticObjectId = Field(
        title="Идентификатор жителя проставившего оценку",
    )
    rate: int = Field(
        ge=1,
        le=5,
        title="Оценка заявки данным жителем",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        title="Время выставления оценки",
    )
