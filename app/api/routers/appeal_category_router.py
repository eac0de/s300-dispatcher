"""
Модуль с роутером для работы с шаблонами заявок
"""

from beanie import PydanticObjectId
from fastapi import APIRouter, Request, status

from api.dependencies.auth import EmployeeDep
from api.qp_translators.appeal_category_qp_translator import (
    DispatcherAppealCategoryQPTranslator,
)
from models.appeal_category.appeal_category import AppealCategory
from schemes.appeal_category import AppealCategoryCUScheme
from services.appeal_category_service import AppealCategoryService

appeal_category_router = APIRouter(
    tags=["appeal_categories"],
)


@appeal_category_router.post(
    path="/",
    status_code=status.HTTP_201_CREATED,
    response_model=AppealCategory,
)
async def create_appeal_category(
    employee: EmployeeDep,
    scheme: AppealCategoryCUScheme,
):
    """
    Создание шаблона описания заявки или ее исполнения
    """

    service = AppealCategoryService(employee)
    return await service.create_appeal_category(scheme)


@appeal_category_router.get(
    path="/",
    description="Получения списка заявок сотрудником.<br>" + DispatcherAppealCategoryQPTranslator.get_docs(),
    status_code=status.HTTP_200_OK,
    response_model=list[AppealCategory],
)
async def get_appeal_category_list(
    req: Request,
    employee: EmployeeDep,
):
    """
    Получение шаблона описания заявки или ее исполнения
    """
    params = await DispatcherAppealCategoryQPTranslator.parse(req.query_params)
    service = AppealCategoryService(employee)
    templates = await service.get_appeal_categories(
        query_list=params.query_list,
        offset=params.offset,
        limit=params.limit,
        sort=params.sort,
    )
    return await templates.to_list()


@appeal_category_router.patch(
    path="/{appeal_category_id}/",
    status_code=status.HTTP_200_OK,
)
async def update_appeal_category(
    employee: EmployeeDep,
    appeal_category_id: PydanticObjectId,
    scheme: AppealCategoryCUScheme,
):
    """
    Обновление шаблона описания заявки или ее исполнения
    """

    service = AppealCategoryService(employee)
    return await service.update_appeal_category(
        appeal_category_id=appeal_category_id,
        scheme=scheme,
    )


@appeal_category_router.delete(
    path="/{appeal_category_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_appeal_category(
    employee: EmployeeDep,
    appeal_category_id: PydanticObjectId,
):
    """
    Удаление шаблона описания заявки или ее исполнения
    """

    service = AppealCategoryService(employee)
    await service.delete_appeal_category(appeal_category_id)
