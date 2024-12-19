from pydantic import BaseModel, Field


class AppealStats(BaseModel):
    run: int = Field(
        title="Количество обращений в работе",
    )
    accepted: int = Field(
        title="Количество полученных обращений",
    )
    performed: int = Field(
        title="Количество выполненных обращений",
    )
    overdue: int = Field(
        title="Количество просроченных обращений",
    )
