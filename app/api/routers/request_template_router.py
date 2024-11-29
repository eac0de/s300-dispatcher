"""
Модуль с роутером для работы с шаблонами заявок
"""

from beanie import PydanticObjectId
from fastapi import APIRouter, status

from api.dependencies.auth import EmployeeDep
from models.request_template.request_template import RequestTemplate
from schemes.request_template_scheme import RequestTemplateCUScheme
from services.request_template_service import RequestTemplateService

request_template_router = APIRouter(
    tags=["request_templates"],
)


@request_template_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=RequestTemplate,
)
async def create_request_template(
    employee: EmployeeDep,
    scheme: RequestTemplateCUScheme,
):
    """
    Создание шаблона описания заявки или ее исполнения
    """

    service = RequestTemplateService(employee)
    return await service.create_template(scheme)


@request_template_router.get(
    path="/",
    status_code=status.HTTP_200_OK,
    response_model=list[RequestTemplate],
)
async def get_request_template_list(
    employee: EmployeeDep,
):
    """
    Получение шаблона описания заявки или ее исполнения
    """

    service = RequestTemplateService(employee)
    return await service.get_template_list()


@request_template_router.patch(
    path="/{request_template_id}/",
    status_code=status.HTTP_200_OK,
)
async def update_request_template(
    employee: EmployeeDep,
    request_template_id: PydanticObjectId,
    scheme: RequestTemplateCUScheme,
):
    """
    Обновление шаблона описания заявки или ее исполнения
    """

    service = RequestTemplateService(employee)
    return await service.update_template(
        request_template_id=request_template_id,
        scheme=scheme,
    )


@request_template_router.delete(
    path="/{request_template_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_request_template(
    employee: EmployeeDep,
    request_template_id: PydanticObjectId,
):
    """
    Удаление шаблона описания заявки или ее исполнения
    """

    service = RequestTemplateService(employee)
    await service.delete_template(request_template_id)
