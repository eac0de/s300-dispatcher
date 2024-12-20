from pydantic import BaseModel, Field


class TenantDebts(BaseModel):
    sector: str = Field(
        title="Сектор",
    )
    debt: int = Field(
        title="Долг",
    )


class TenantStats(BaseModel):
    debts: list[TenantDebts] = Field(
        default_factory=list,
        title="Долги жителя",
    )
    rates: int = Field(
        title="Оценки жителю",
    )


class RequestTenantStats(TenantStats):
    request_stats: int = Field(
        title="Статистика заявок жителя",
    )
