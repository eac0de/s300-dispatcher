from typing import Literal

from pydantic import BaseModel, Field


class TenantRatingRScheme(BaseModel):
    up: int = Field(
        title="Количество пальцев вверх",
    )
    down: int = Field(
        title="Количество пальцев вниз",
    )
    current_rate: Literal["up", "down"] | None = Field(
        title="Количество пальцев вниз",
    )
