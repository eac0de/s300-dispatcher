"""
Модуль с роутером для работы с сторонними лицами, сотрудниками и организациями
"""

from beanie import PydanticObjectId
from fastapi import APIRouter, Request
from starlette import status

from api.dependencies.auth import EmployeeDep
from api.filters.other_filter import (
    OtherEmployeeFilter,
    OtherPersonFilter,
    OtherProviderFilter,
)
from schemes.other import (
    OtherEmployeeCUScheme,
    OtherEmployeeRScheme,
    OtherPersonCUScheme,
    OtherPersonRScheme,
    OtherProviderCUScheme,
    OtherProviderRScheme,
)
from services.other_service import OtherService

other_router = APIRouter(
    tags=["others"],
)


@other_router.get(
    path="/persons",
    status_code=status.HTTP_200_OK,
    response_model=list[OtherPersonRScheme],
)
async def get_other_persons_list(
    employee: EmployeeDep,
    req: Request,
):
    """
    Получение списка сторонних лиц.
    Для фильтрации есть определенные фильтры см. в модуле api/filters/other_filter
    """

    params = await OtherPersonFilter.parse_query_params(req.query_params)
    service = OtherService(employee)
    other_persons_list = await service.get_other_persons_list(
        query_list=params.query_list,
        offset=params.offset,
        limit=params.limit,
        sort=params.sort,
    )
    return other_persons_list


@other_router.post(
    path="/persons",
    status_code=status.HTTP_201_CREATED,
    response_model=OtherPersonRScheme,
)
async def create_other_person(
    employee: EmployeeDep,
    scheme: OtherPersonCUScheme,
):
    """
    Создание стороннего лица
    """

    service = OtherService(employee)
    other_person = await service.create_other_person(scheme)
    return other_person


@other_router.put(
    path="/persons/{other_person_id}",
    status_code=status.HTTP_200_OK,
    response_model=OtherPersonRScheme,
)
async def update_other_person(
    employee: EmployeeDep,
    other_person_id: PydanticObjectId,
    scheme: OtherPersonCUScheme,
):
    """
    Обновление стороннего лица
    """

    service = OtherService(employee)
    other_person = await service.update_other_person(
        other_person_id=other_person_id,
        scheme=scheme,
    )
    return other_person


@other_router.delete(
    path="/persons/{other_person_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_other_person(
    employee: EmployeeDep,
    other_person_id: PydanticObjectId,
):
    """
    Удаление стороннего лица
    """

    service = OtherService(employee)
    await service.delete_other_person(other_person_id)


@other_router.get(
    path="/employees",
    status_code=status.HTTP_200_OK,
    response_model=list[OtherEmployeeRScheme],
)
async def get_other_employees_list(
    employee: EmployeeDep,
    req: Request,
):
    """
    Получение списка сторонних сотрудников.
    Для фильтрации есть определенные фильтры см. в модуле api/filters/other_filter
    """

    params = await OtherEmployeeFilter.parse_query_params(req.query_params)
    service = OtherService(employee)
    other_employees_list = await service.get_other_employees_list(
        query_list=params.query_list,
        offset=params.offset,
        limit=params.limit,
        sort=params.sort,
    )
    return other_employees_list


@other_router.post(
    path="/employees",
    status_code=status.HTTP_201_CREATED,
    response_model=OtherEmployeeRScheme,
)
async def create_other_employee(
    employee: EmployeeDep,
    scheme: OtherEmployeeCUScheme,
):
    """
    Создание стороннего сотрудника
    """

    service = OtherService(employee)
    other_employee = await service.create_other_employee(scheme)
    return other_employee


@other_router.put(
    path="/employees/{other_employee_id}",
    status_code=status.HTTP_200_OK,
    response_model=OtherEmployeeRScheme,
)
async def update_other_employee(
    employee: EmployeeDep,
    other_employee_id: PydanticObjectId,
    scheme: OtherEmployeeCUScheme,
):
    """
    Обновление стороннего сотрудника
    """

    service = OtherService(employee)
    other_employee = await service.update_other_employee(
        other_employee_id=other_employee_id,
        scheme=scheme,
    )
    return other_employee


@other_router.delete(
    path="/employees/{other_employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_other_employee(
    employee: EmployeeDep,
    other_employee_id: PydanticObjectId,
):
    """
    Удаление стороннего сотрудника
    """

    service = OtherService(employee)
    await service.delete_other_employee(other_employee_id)


@other_router.get(
    path="/providers",
    status_code=status.HTTP_200_OK,
    response_model=list[OtherProviderRScheme],
)
async def get_other_providers_list(
    employee: EmployeeDep,
    req: Request,
):
    """
    Получение списка сторонних организаций.
    Для фильтрации есть определенные фильтры см. в модуле api/filters/other_filter
    """

    params = await OtherProviderFilter.parse_query_params(req.query_params)
    service = OtherService(employee)
    other_providers_list = await service.get_other_providers_list(
        query_list=params.query_list,
        offset=params.offset,
        limit=params.limit,
        sort=params.sort,
    )
    return other_providers_list


@other_router.post(
    path="/providers",
    status_code=status.HTTP_201_CREATED,
    response_model=OtherProviderRScheme,
)
async def create_other_provider(
    employee: EmployeeDep,
    scheme: OtherProviderCUScheme,
):
    """
    Создание сторонней организации
    """

    service = OtherService(employee)
    other_provider = await service.create_other_provider(scheme)
    return other_provider


@other_router.put(
    path="/providers/{other_provider_id}",
    status_code=status.HTTP_200_OK,
    response_model=OtherProviderRScheme,
)
async def update_other_provider(
    employee: EmployeeDep,
    other_provider_id: PydanticObjectId,
    scheme: OtherProviderCUScheme,
):
    """
    Обновление сторонней организации
    """

    service = OtherService(employee)
    other_employee = await service.update_other_provider(
        other_provider_id=other_provider_id,
        scheme=scheme,
    )
    return other_employee


@other_router.delete(
    path="/providers/{other_provider_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_other_provider(
    employee: EmployeeDep,
    other_provider_id: PydanticObjectId,
):
    """
    Удаление сторонней организации
    """

    service = OtherService(employee)
    await service.delete_other_provider(other_provider_id)