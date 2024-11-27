from pydantic import BaseModel, Field


class RequestStats(BaseModel):
    run: int = Field(
        title="Количество аварийных заявок",
    )
    accepted: int = Field(
        title="Количество аварийных заявок",
    )
    emergency: int = Field(
        title="Количество аварийных заявок",
    )
    overdue: int = Field(
        title="Количество просроченных заявок",
    )
