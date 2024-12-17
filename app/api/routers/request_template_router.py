"""
Модуль с роутером для работы с шаблонами заявок
"""

from beanie import PydanticObjectId
from fastapi import APIRouter, Request, status

from api.dependencies.auth import EmployeeDep
from api.qp_translators.request_template_qp_translator import (
    DispatcherRequestTemplateQPTranslator,
)
from schemes.request_template import RequestTemplateCUScheme, RequestTemplateRLScheme
from services.request_template_service import RequestTemplateService

request_template_router = APIRouter(
    tags=["request_templates"],
)


@request_template_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=RequestTemplateRLScheme,
)
async def create_request_template(
    employee: EmployeeDep,
    scheme: RequestTemplateCUScheme,
):
    """
    Создание шаблона описания заявки или ее исполнения
    """

    service = RequestTemplateService(employee)
    return await service.create_request_template(scheme)


@request_template_router.get(
    path="/",
    description="Получения списка заявок сотрудником.<br>" + DispatcherRequestTemplateQPTranslator.get_docs(),
    status_code=status.HTTP_200_OK,
    response_model=list[RequestTemplateRLScheme],
)
async def get_request_template_list(
    req: Request,
    employee: EmployeeDep,
):
    """
    Получение шаблона описания заявки или ее исполнения
    """
    params = await DispatcherRequestTemplateQPTranslator.parse(req.query_params)
    service = RequestTemplateService(employee)
    templates = await service.get_request_templates(
        query_list=params.query_list,
        offset=params.offset,
        limit=params.limit,
        sort=params.sort,
    )
    return await templates.to_list()


@request_template_router.patch(
    path="/{request_template_id}/",
    status_code=status.HTTP_200_OK,
    response_model=RequestTemplateRLScheme,
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
    return await service.update_request_template(
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
    await service.delete_request_template(request_template_id)
