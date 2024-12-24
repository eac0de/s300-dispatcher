from typing import Literal

from pydantic import BaseModel, Field


class DebtTenantStats(BaseModel):
    sector: str = Field(
        title="Сектор",
    )
    amount: int = Field(
        title="Сумма долга",
    )


class RatesTenantStats(BaseModel):
    up: int = Field(
        title="Количество пальцев вверх",
    )
    down: int = Field(
        title="Количество пальцев вниз",
    )
    current_rate: Literal["up", "down"] | None = Field(
        title="Количество пальцев вниз",
    )


class TenantStats(BaseModel):
    debts: list[DebtTenantStats] = Field(
        default_factory=list,
        title="Долги жителя",
    )
    rates: RatesTenantStats = Field(
        title="Оценки жителю",
    )


class TenantRequestStats(BaseModel):
    tenant: int = Field(
        title="Долги жителя",
    )
    area: int = Field(
        title="Долги жителя",
    )
    house: int = Field(
        title="Долги жителя",
    )
    type_area: int = Field(
        title="Долги жителя",
    )


class TenantStatsWithRequestStats(TenantStats):
    request_stats: TenantRequestStats = Field(
        title="Статистика заявок жителя",
    )
