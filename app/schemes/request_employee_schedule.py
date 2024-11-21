"""
Модуль со схемами отображения графика работы работников
"""

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class RequestEmployeeWeeklySchedule(BaseModel):
    """
    Класс схемы отображения недельного графика работы работника
    """

    employee_id: PydanticObjectId
    workload: list[int] = Field(
        default_factory=lambda: [0] * 7,
        min_length=7,
        max_length=7,
    )


class RequestEmployeeDailySchedule(BaseModel):
    """
    Класс схемы отображения дневного графика работы работника
    """

    employee_id: PydanticObjectId
    workload: list[list[str]] = Field(
        default_factory=lambda: [[] for _ in range(96)],
        min_length=96,
        max_length=96,
    )
