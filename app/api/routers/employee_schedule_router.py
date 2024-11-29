"""
Модуль с роутером для получения информации о расписании работ с заявками сотрудников
"""

from datetime import datetime

from beanie import PydanticObjectId
from fastapi import APIRouter, Query, status

from api.dependencies.auth import EmployeeDep
from schemes.request_employee_schedule import (
    RequestEmployeeDailySchedule,
    RequestEmployeeWeeklySchedule,
)
from services.request.dispatcher_request_service import DispatcherRequestService

employee_schedule_router = APIRouter(
    tags=["employee_request_schedules"],
)


@employee_schedule_router.get(
    path="/weekly/",
    status_code=status.HTTP_200_OK,
    response_model=list[RequestEmployeeWeeklySchedule],
)
async def get_request_employee_weekly_schedules(
    employee: EmployeeDep,
    start_at: datetime = Query(),
    employee_ids: set[PydanticObjectId] = Query(
        min_length=1,
        max_length=10,
    ),
):
    """
    Получение графиков работы с заявками сотрудников на 1 неделю от заданной даты
    """

    service = DispatcherRequestService(employee)
    employee_weekly_schedules = await service.get_request_employee_weekly_schedules(
        start_at=start_at,
        employee_ids=employee_ids,
    )
    return employee_weekly_schedules


@employee_schedule_router.get(
    path="/daily/",
    status_code=status.HTTP_200_OK,
    response_model=list[RequestEmployeeDailySchedule],
)
async def get_request_employee_daily_schedules(
    employee: EmployeeDep,
    start_at: datetime = Query(),
    employee_ids: set[PydanticObjectId] = Query(
        min_length=1,
    ),
):
    """
    Получение графиков работы с заявками сотрудников на 1 день от заданной даты с разбивкой по 15 минут
    """

    service = DispatcherRequestService(employee)
    employee_daily_schedules = await service.get_request_employee_daily_schedules(
        start_at=start_at,
        employee_ids=employee_ids,
    )
    return employee_daily_schedules
